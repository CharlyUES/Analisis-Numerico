from flask import jsonify
import  sympy as sp
import numpy as np
from ......extras.Funciones import errores, secante, respuesta_json, verificaciones
from modelos.extras.latex import conversla

class metodo_secante():
    @staticmethod
    def calcular_secante(json_data):
        x = sp.symbols("x")
        #instanciar respuesta json
        instancia_respuesta = respuesta_json()

        #Verificar la funcion obtenida
        try:
            #Ecuaion de la funcion
            f_x = conversla.latex_(json_data["latex"])
            resultado = f_x.subs(x, 2)
            if resultado > 0:
                pass
        except sp.SympifyError:
            resp = instancia_respuesta.responder_error("Error en la funcion ingresada")
            return jsonify(resp), 400
        except TypeError as e:
            resp = instancia_respuesta.responder_error("Error en la funcion ingresada")
            return jsonify(resp), 400

        #verificar que sea grado mayor a 0
        if verificaciones.obtener_grado(f_x) != None:#es porq es polinomica sino no importa el grado
            if verificaciones.obtener_grado(f_x) < 1:
                resp = instancia_respuesta.responder_error("La función debe ser de grado 1 o mayor")
                return jsonify(resp), 400

        try:
            x_anterior = float(json_data["xi"])
            x_actual = float(json_data["xu"])
            error_aceptado = float(json_data["tolerancia"])
        except ValueError as e:
            resp = instancia_respuesta.responder_error("Error en los datos ingresados" + str(e))
            return jsonify(resp), 400
        except Exception as e:
            resp = instancia_respuesta.responder_error("Error en los datos ingresados" + str(e))
            return jsonify(resp), 400
            
        #metodo de la secante
        try:
            x_calculada = 0
            error_acomulado = 100
            iteracion = 0

            instancia_respuesta.agregar_titulo1("Secante")
            instancia_respuesta.agregar_parrafo("")
            instancia_respuesta.crear_tabla()
            instancia_respuesta.agregar_fila(['Iteracion', 'X0', 'X1', 'F(x0)', 'F(x1)', 'Xr','Error'])

            while True:
                iteracion += 1
                f_x_evaluada_anterior = f_x.subs(x, x_anterior)
                f_x_evaluada_actual = f_x.subs(x, x_actual)
                x_calculada = secante.aproximacion(f_x_evaluada_anterior,f_x_evaluada_actual,x_anterior,x_actual)
                x_calculada = sp.N(x_calculada)
                if x_calculada == 0:
                    instancia_respuesta.agregar_parrafo(f"El valor calculado de x es 0, en la iteracion #{iteracion}, por lo tanto no se puede realizar el calculo del error acomulado")
                    instancia_respuesta.agregar_fila([iteracion, x_anterior, x_actual, f_x_evaluada_anterior, f_x_evaluada_actual, x_calculada, "No se puede calcular"])
                    instancia_respuesta.agregar_titulo1("Se muestra la tabla de iteraciones")
                    instancia_respuesta.agregar_tabla()
                    resp= instancia_respuesta.obtener_y_limpiar_respuesta()
                    return jsonify(resp), 200
                error_acomulado = errores.error_aproximado_porcentual(x_actual,x_calculada)
                error_acomulado = sp.N(error_acomulado)
                instancia_respuesta.agregar_fila([iteracion, x_anterior, x_actual, f_x_evaluada_anterior, f_x_evaluada_actual, x_calculada, error_acomulado])
                x_anterior = x_actual
                x_actual = x_calculada
                if(error_acomulado < error_aceptado):
                    break
                if iteracion > 300:
                    resp = instancia_respuesta.responder_error("El metodo sobrepaso el numero de iteraciones permitidas")
                    return jsonify(resp), 400
                
            instancia_respuesta.agregar_tabla()
            resp = instancia_respuesta.obtener_y_limpiar_respuesta()
            return jsonify(resp), 200
        except Exception as e:
            resp = instancia_respuesta.responder_error("Error en el codigo:\n " + str(e) + " " + str(e.with_traceback))
            return jsonify(resp), 500





