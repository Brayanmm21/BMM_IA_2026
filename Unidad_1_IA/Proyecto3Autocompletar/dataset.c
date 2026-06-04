#include <stdio.h>

// Funcion: sumar dos numeros
int funcion_sumar(int numero_a, int numero_b) {
    int resultado = 0;
    resultado = numero_a + numero_b;
    return resultado;
}

// Funcion: restar dos numeros
int funcion_restar(int numero_a, int numero_b) {
    int resultado = 0;
    resultado = numero_a - numero_b;
    return resultado;
}

// Funcion: multiplicar dos numeros
int funcion_multiplicar(int numero_a, int numero_b) {
    int resultado = 0;
    resultado = numero_a * numero_b;
    return resultado;
}

// Funcion: dividir dos numeros
int funcion_dividir(int numero_a, int numero_b) {
    int resultado = 0;
    if (numero_b != 0) {
        resultado = numero_a / numero_b;
    }
    return resultado;
}

// Funcion: calcular doble
int funcion_doble(int numero) {
    int resultado = 0;
    resultado = numero * 2;
    return resultado;
}

// Funcion: calcular triple
int funcion_triple(int numero) {
    int resultado = 0;
    resultado = numero * 3;
    return resultado;
}

// Funcion: calcular cuadrado
int funcion_cuadrado(int numero) {
    int resultado = 0;
    resultado = numero * numero;
    return resultado;
}

// Funcion: calcular cubo
int funcion_cubo(int numero) {
    int resultado = 0;
    resultado = numero * numero * numero;
    return resultado;
}

// Funcion: sumar cinco
int funcion_sumar_cinco(int numero) {
    int resultado = 0;
    resultado = numero + 5;
    return resultado;
}

// Funcion: restar cinco
int funcion_restar_cinco(int numero) {
    int resultado = 0;
    resultado = numero - 5;
    return resultado;
}

// Funcion: verificar par
int funcion_es_par(int numero) {
    int resultado = 0;
    if (numero % 2 == 0) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: verificar impar
int funcion_es_impar(int numero) {
    int resultado = 0;
    if (numero % 2 != 0) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: verificar positivo
int funcion_es_positivo(int numero) {
    int resultado = 0;
    if (numero > 0) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: verificar negativo
int funcion_es_negativo(int numero) {
    int resultado = 0;
    if (numero < 0) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: verificar cero
int funcion_es_cero(int numero) {
    int resultado = 0;
    if (numero == 0) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: obtener mayor
int funcion_mayor(int numero_a, int numero_b) {
    int resultado = 0;
    if (numero_a > numero_b) {
        resultado = numero_a;
    } else {
        resultado = numero_b;
    }
    return resultado;
}

// Funcion: obtener menor
int funcion_menor(int numero_a, int numero_b) {
    int resultado = 0;
    if (numero_a < numero_b) {
        resultado = numero_a;
    } else {
        resultado = numero_b;
    }
    return resultado;
}

// Funcion: calcular promedio
int funcion_promedio(int numero_a, int numero_b) {
    int resultado = 0;
    resultado = (numero_a + numero_b) / 2;
    return resultado;
}

// Funcion: valor absoluto
int funcion_absoluto(int numero) {
    int resultado = 0;
    if (numero < 0) {
        resultado = numero * -1;
    } else {
        resultado = numero;
    }
    return resultado;
}

// Funcion: verificar mayor que cien
int funcion_mayor_cien(int numero) {
    int resultado = 0;
    if (numero > 100) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: verificar menor que cien
int funcion_menor_cien(int numero) {
    int resultado = 0;
    if (numero < 100) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: verificar multiplo de tres
int funcion_multiplo_tres(int numero) {
    int resultado = 0;
    if (numero % 3 == 0) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: verificar multiplo de cinco
int funcion_multiplo_cinco(int numero) {
    int resultado = 0;
    if (numero % 5 == 0) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: verificar multiplo de diez
int funcion_multiplo_diez(int numero) {
    int resultado = 0;
    if (numero % 10 == 0) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: calcular residuo
int funcion_residuo(int numero_a, int numero_b) {
    int resultado = 0;
    if (numero_b != 0) {
        resultado = numero_a % numero_b;
    }
    return resultado;
}

// Funcion: calcular area cuadrado
int funcion_area_cuadrado(int lado) {
    int resultado = 0;
    resultado = lado * lado;
    return resultado;
}

// Funcion: calcular perimetro cuadrado
int funcion_perimetro_cuadrado(int lado) {
    int resultado = 0;
    resultado = lado * 4;
    return resultado;
}

// Funcion: calcular area rectangulo
int funcion_area_rectangulo(int base, int altura) {
    int resultado = 0;
    resultado = base * altura;
    return resultado;
}

// Funcion: calcular perimetro rectangulo
int funcion_perimetro_rectangulo(int base, int altura) {
    int resultado = 0;
    resultado = (base * 2) + (altura * 2);
    return resultado;
}

// Funcion: calcular area triangulo
int funcion_area_triangulo(int base, int altura) {
    int resultado = 0;
    resultado = (base * altura) / 2;
    return resultado;
}

// Funcion: sumar numeros hasta limite
int funcion_sumar_hasta(int limite) {
    int resultado = 0;
    int contador = 0;
    for (contador = 1; contador <= limite; contador++) {
        resultado = resultado + contador;
    }
    return resultado;
}

// Funcion: sumar pares hasta limite
int funcion_sumar_pares(int limite) {
    int resultado = 0;
    int contador = 0;
    for (contador = 0; contador <= limite; contador++) {
        if (contador % 2 == 0) {
            resultado = resultado + contador;
        }
    }
    return resultado;
}

// Funcion: sumar impares hasta limite
int funcion_sumar_impares(int limite) {
    int resultado = 0;
    int contador = 0;
    for (contador = 0; contador <= limite; contador++) {
        if (contador % 2 != 0) {
            resultado = resultado + contador;
        }
    }
    return resultado;
}

// Funcion: contar pares hasta limite
int funcion_contar_pares(int limite) {
    int resultado = 0;
    int contador = 0;
    for (contador = 0; contador <= limite; contador++) {
        if (contador % 2 == 0) {
            resultado = resultado + 1;
        }
    }
    return resultado;
}

// Funcion: contar impares hasta limite
int funcion_contar_impares(int limite) {
    int resultado = 0;
    int contador = 0;
    for (contador = 0; contador <= limite; contador++) {
        if (contador % 2 != 0) {
            resultado = resultado + 1;
        }
    }
    return resultado;
}

// Funcion: calcular factorial
int funcion_factorial(int numero) {
    int resultado = 1;
    int contador = 0;
    for (contador = 1; contador <= numero; contador++) {
        resultado = resultado * contador;
    }
    return resultado;
}

// Funcion: contar digitos
int funcion_contar_digitos(int numero) {
    int resultado = 0;
    while (numero != 0) {
        numero = numero / 10;
        resultado = resultado + 1;
    }
    return resultado;
}

// Funcion: sumar digitos
int funcion_sumar_digitos(int numero) {
    int resultado = 0;
    int digito = 0;
    while (numero != 0) {
        digito = numero % 10;
        resultado = resultado + digito;
        numero = numero / 10;
    }
    return resultado;
}

// Funcion: invertir numero
int funcion_invertir_numero(int numero) {
    int resultado = 0;
    int digito = 0;
    while (numero != 0) {
        digito = numero % 10;
        resultado = resultado * 10 + digito;
        numero = numero / 10;
    }
    return resultado;
}

// Funcion: mayor de tres numeros
int funcion_mayor_tres(int numero_a, int numero_b, int numero_c) {
    int resultado = numero_a;
    if (numero_b > resultado) {
        resultado = numero_b;
    }
    if (numero_c > resultado) {
        resultado = numero_c;
    }
    return resultado;
}

// Funcion: menor de tres numeros
int funcion_menor_tres(int numero_a, int numero_b, int numero_c) {
    int resultado = numero_a;
    if (numero_b < resultado) {
        resultado = numero_b;
    }
    if (numero_c < resultado) {
        resultado = numero_c;
    }
    return resultado;
}

// Funcion: buscar valor en arreglo
int funcion_buscar_arreglo(int arreglo[], int tamano, int valor) {
    int resultado = 0;
    int contador = 0;
    for (contador = 0; contador < tamano; contador++) {
        if (arreglo[contador] == valor) {
            resultado = 1;
        }
    }
    return resultado;
}

// Funcion: sumar valores de arreglo
int funcion_sumar_arreglo(int arreglo[], int tamano) {
    int resultado = 0;
    int contador = 0;
    for (contador = 0; contador < tamano; contador++) {
        resultado = resultado + arreglo[contador];
    }
    return resultado;
}

// Funcion: promedio de arreglo
int funcion_promedio_arreglo(int arreglo[], int tamano) {
    int resultado = 0;
    if (tamano != 0) {
        resultado = funcion_sumar_arreglo(arreglo, tamano) / tamano;
    }
    return resultado;
}

// Funcion: mayor valor de arreglo
int funcion_mayor_arreglo(int arreglo[], int tamano) {
    int resultado = arreglo[0];
    int contador = 0;
    for (contador = 1; contador < tamano; contador++) {
        if (arreglo[contador] > resultado) {
            resultado = arreglo[contador];
        }
    }
    return resultado;
}

// Funcion: menor valor de arreglo
int funcion_menor_arreglo(int arreglo[], int tamano) {
    int resultado = arreglo[0];
    int contador = 0;
    for (contador = 1; contador < tamano; contador++) {
        if (arreglo[contador] < resultado) {
            resultado = arreglo[contador];
        }
    }
    return resultado;
}

// Funcion: contar valor en arreglo
int funcion_contar_valor(int arreglo[], int tamano, int valor) {
    int resultado = 0;
    int contador = 0;
    for (contador = 0; contador < tamano; contador++) {
        if (arreglo[contador] == valor) {
            resultado = resultado + 1;
        }
    }
    return resultado;
}

// Funcion: multiplicar valores de arreglo
int funcion_multiplicar_arreglo(int arreglo[], int tamano) {
    int resultado = 1;
    int contador = 0;
    for (contador = 0; contador < tamano; contador++) {
        resultado = resultado * arreglo[contador];
    }
    return resultado;
}

// Funcion: convertir minutos a segundos
int funcion_minutos_segundos(int minutos) {
    int resultado = 0;
    resultado = minutos * 60;
    return resultado;
}

// Funcion: convertir horas a minutos
int funcion_horas_minutos(int horas) {
    int resultado = 0;
    resultado = horas * 60;
    return resultado;
}

// Funcion: convertir horas a segundos
int funcion_horas_segundos(int horas) {
    int resultado = 0;
    resultado = horas * 3600;
    return resultado;
}

// Funcion: convertir metros a centimetros
int funcion_metros_centimetros(int metros) {
    int resultado = 0;
    resultado = metros * 100;
    return resultado;
}

// Funcion: convertir kilometros a metros
int funcion_kilometros_metros(int kilometros) {
    int resultado = 0;
    resultado = kilometros * 1000;
    return resultado;
}

// Funcion: calcular descuento
int funcion_calcular_descuento(int precio, int porcentaje) {
    int resultado = 0;
    resultado = precio - ((precio * porcentaje) / 100);
    return resultado;
}

// Funcion: calcular porcentaje
int funcion_calcular_porcentaje(int cantidad, int porcentaje) {
    int resultado = 0;
    resultado = (cantidad * porcentaje) / 100;
    return resultado;
}

// Funcion: verificar rango basico
int funcion_rango_basico(int numero) {
    int resultado = 0;
    if (numero >= 1 && numero <= 10) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: verificar edad mayor
int funcion_edad_mayor(int edad) {
    int resultado = 0;
    if (edad >= 18) {
        resultado = 1;
    }
    return resultado;
}

// Funcion: calcular promedio tres
int funcion_promedio_tres(int numero_a, int numero_b, int numero_c) {
    int resultado = 0;
    resultado = (numero_a + numero_b + numero_c) / 3;
    return resultado;
}

// Funcion: calcular suma triple
int funcion_suma_triple(int numero_a, int numero_b, int numero_c) {
    int resultado = 0;
    resultado = numero_a + numero_b + numero_c;
    return resultado;
}

// Funcion: verificar divisible
int funcion_es_divisible(int numero_a, int numero_b) {
    int resultado = 0;
    if (numero_b != 0) {
        if (numero_a % numero_b == 0) {
            resultado = 1;
        }
    }
    return resultado;
}

// Funcion: calcular potencia simple
int funcion_potencia_simple(int base, int exponente) {
    int resultado = 1;
    int contador = 0;
    for (contador = 0; contador < exponente; contador++) {
        resultado = resultado * base;
    }
    return resultado;
}