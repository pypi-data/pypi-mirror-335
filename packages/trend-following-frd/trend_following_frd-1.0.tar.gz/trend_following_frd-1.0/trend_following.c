// trend_following.c

#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include <math.h>

// Función auxiliar para calcular EMA
static void calculate_ema(double *prices, double *ema, int length, int span) {
    double alpha = 2.0 / (span + 1.0);
    ema[0] = prices[0]; // Primer valor
    
    for (int i = 1; i < length; i++) {
        ema[i] = prices[i] * alpha + ema[i - 1] * (1.0 - alpha);
    }
}

// Función auxiliar para convertir dictionary Python a serie mensual
static PyObject* get_monthly_series(PyObject *daily_values) {
    // Esta función debe ser implementada en Python o usar PyObject directamente
    // Ya que involucra manipulación de fechas y agrupación que es compleja en C puro
    
    // Asumimos que tienes una función en Python llamada 'get_monthly_series'
    PyObject *module = PyImport_ImportModule("utils");
    if (module == NULL) {
        PyErr_SetString(PyExc_ImportError, "No se pudo importar el módulo que contiene get_monthly_series");
        return NULL;
    }
    
    PyObject *func = PyObject_GetAttrString(module, "get_monthly_series");
    Py_DECREF(module);
    if (func == NULL) {
        PyErr_SetString(PyExc_AttributeError, "No se encontró la función get_monthly_series");
        return NULL;
    }
    
    PyObject *result = PyObject_CallFunctionObjArgs(func, daily_values, NULL);
    Py_DECREF(func);
    return result;
}

// Función principal de backtest
static PyObject* trend_following_backtest_monthly(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *data_obj;
    double initial_capital;
    int short_window = 10;
    int long_window = 30;
    double commission_rate = 0.001;
    
    static char *kwlist[] = {"data", "initial_capital", "short_window", "long_window", "commission_rate", NULL};
    
    // Parsear argumentos
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Od|iid", kwlist,
                                     &data_obj, &initial_capital,
                                     &short_window, &long_window, &commission_rate)) {
        return NULL;
    }
    
    // Verificar que data es un DataFrame de pandas
    int has_iloc = PyObject_HasAttrString(data_obj, "iloc");
    if (!has_iloc) {
        PyErr_SetString(PyExc_TypeError, "El primer argumento debe ser un DataFrame de pandas");
        return NULL;
    }
    
    // Obtener la columna 'Close' y convertirla a un array de numpy
    PyObject *close_col = PyObject_GetAttrString(data_obj, "Close");
    if (close_col == NULL) {
        PyErr_SetString(PyExc_AttributeError, "No se encontró la columna 'Close' en el DataFrame");
        return NULL;
    }
    
    // Obtener el índice (fechas) del DataFrame
    PyObject *index = PyObject_GetAttrString(data_obj, "index");
    if (index == NULL) {
        Py_DECREF(close_col);
        PyErr_SetString(PyExc_AttributeError, "No se pudo obtener el índice del DataFrame");
        return NULL;
    }
    
    // Convertir columna Close a array NumPy
    PyObject *close_array = PyObject_GetAttrString(close_col, "values");
    Py_DECREF(close_col);
    if (close_array == NULL) {
        Py_DECREF(index);
        PyErr_SetString(PyExc_AttributeError, "No se pudo convertir Close a array");
        return NULL;
    }
    
    // Obtener longitud de los datos
    Py_ssize_t length = PyArray_SIZE((PyArrayObject *)close_array);
    
    // Crear arrays para EMA
    double *prices = (double *)malloc(length * sizeof(double));
    double *ema_short = (double *)malloc(length * sizeof(double));
    double *ema_long = (double *)malloc(length * sizeof(double));
    
    if (prices == NULL || ema_short == NULL || ema_long == NULL) {
        free(prices);
        free(ema_short);
        free(ema_long);
        Py_DECREF(close_array);
        Py_DECREF(index);
        PyErr_SetString(PyExc_MemoryError, "No se pudo asignar memoria para los arrays");
        return NULL;
    }
    
    // Copiar precios al array C
    for (Py_ssize_t i = 0; i < length; i++) {
        PyObject *price_obj = PyArray_GETITEM((PyArrayObject *)close_array, PyArray_GETPTR1((PyArrayObject *)close_array, i));
        prices[i] = PyFloat_AsDouble(price_obj);
        Py_DECREF(price_obj);
    }
    
    // Calcular EMAs
    calculate_ema(prices, ema_short, length, short_window);
    calculate_ema(prices, ema_long, length, long_window);
    
    // Crear diccionario Python para almacenar valores diarios
    PyObject *daily_values = PyDict_New();
    
    // Variables de backtest
    double capital = initial_capital;
    double shares = 0.0;
    int position = 0;  // 0: sin posición, 1: posición larga
    
    // Ejecutar backtest
    for (Py_ssize_t i = 1; i < length; i++) {
        // Obtener fecha actual
        PyObject *date = PyObject_GetItem(index, PyLong_FromSsize_t(i));
        double price = prices[i];
        
        double prev_short = ema_short[i-1];
        double prev_long = ema_long[i-1];
        double curr_short = ema_short[i];
        double curr_long = ema_long[i];
        
        // Guardar el valor diario
        double portfolio_value = capital + shares * price;
        PyDict_SetItem(daily_values, date, PyFloat_FromDouble(portfolio_value));
        Py_DECREF(date);
        
        // Señal de compra: cruce al alza
        if (curr_short > curr_long && prev_short <= prev_long && position == 0) {
            // Calcular la cantidad de acciones considerando la comisión de compra
            shares = capital / (price * (1 + commission_rate));
            // Al comprar se utiliza todo el capital
            capital = 0;
            position = 1;
        }
        // Señal de venta: cruce a la baja
        else if (curr_short < curr_long && prev_short >= prev_long && position == 1) {
            double gross_proceeds = shares * price;
            double commission_fee = gross_proceeds * commission_rate;
            double net_proceeds = gross_proceeds - commission_fee;
            capital = net_proceeds;
            shares = 0;
            position = 0;
        }
    }
    
    // Liberar memoria de los arrays
    free(prices);
    free(ema_short);
    free(ema_long);
    Py_DECREF(close_array);
    Py_DECREF(index);
    
    // Convertir a serie mensual
    PyObject *monthly = get_monthly_series(daily_values);
    Py_DECREF(daily_values);
    
    return monthly;
}

// Métodos del módulo
static PyMethodDef TrendFollowingMethods[] = {
    {"trend_following_backtest_monthly", (PyCFunction)trend_following_backtest_monthly, 
     METH_VARARGS | METH_KEYWORDS, "Realiza backtest de estrategia de seguimiento de tendencia con EMAs"},
    {NULL, NULL, 0, NULL}  // Sentinel
};

// Definición del módulo
static struct PyModuleDef trendmodule = {
    PyModuleDef_HEAD_INIT,
    "trend_following",  // Nombre del módulo
    "Módulo para backtesting de estrategias de trading",  // Documentación
    -1,
    TrendFollowingMethods
};

// Función de inicialización
PyMODINIT_FUNC PyInit_trend_following(void) {
    PyObject *m;
    
    m = PyModule_Create(&trendmodule);
    if (m == NULL)
        return NULL;

    // Importar numpy
    import_array();
    
    return m;
}