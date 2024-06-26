from flask import jsonify
import  sympy as sp
from ......extras.Funciones import errores, newton_modificado, respuesta_json, verificaciones, commprobaciones_json
from modelos.extras.latex import conversla_html

class metodo_newton_modificado():
    @staticmethod
    def calcular_newton_modificado(json_data):
        
        x = sp.symbols("x")
        #instanciar respuesta json
        instancia_respuesta = respuesta_json()

        try:
            #Verificar la funcion obtenida
            response, status_code = commprobaciones_json.comprobar_funcionX_latex(json_data, instancia_respuesta)
            if status_code != 200:
                resp = response
                return resp, 400
            f_x = response
        except Exception as e:
            resp = instancia_respuesta.responder_error("Error al obtener la función ingresada: "+str(e))
            return jsonify(resp), 400

        #verificar que sea grado mayor a 0
        if verificaciones.obtener_grado(f_x) != None: #es porq es polinomica sino no importa el grado
            if verificaciones.obtener_grado(f_x) < 1:
                resp = instancia_respuesta.responder_error("La función debe ser de grado 1 o mayor")
                return jsonify(resp), 400
            
        try:
            x_actual = float(json_data["xi"])
            error_aceptado = float(json_data["tolerancia"])
        except ValueError as e:
            resp = instancia_respuesta.responder_error("Error en los datos ingresados" + str(e))
            return jsonify(resp), 400
        except Exception as e:
            resp = instancia_respuesta.responder_error("Error en los datos ingresados" + str(e))
            return jsonify(resp), 400
            
        try:
            f_prima = sp.diff(f_x)
            f_prima_prima = sp.diff(f_prima)
        
            x_anterior = 0
            error_acomulado = 100
            iteracion = 0

            f_prima_evaluada = f_prima.subs(x, x_actual)
            f_x_evaluada = f_x.subs(x, x_actual)
            f_prima_prima_evaluada = f_prima_prima.subs(x, x_actual)
            criterio = abs((f_x_evaluada*f_prima_prima_evaluada)/(f_prima_evaluada**2))
            if criterio > 1:
                resp = instancia_respuesta.responder_error("El criterio de convergencia no se cumple")
                return jsonify(resp), 400

            instancia_respuesta.agregar_titulo1("Valores iniciales")
            instancia_respuesta.agregar_parrafo("Función ingresada: " + conversla_html.mathl_(f_x))
            instancia_respuesta.agregar_parrafo("Se muestra la tabla de iteraciones")
            instancia_respuesta.crear_tabla()
            instancia_respuesta.agregar_fila(['Iteracion', 'X0', 'F(x0)', 'F\'(x0)', 'F\'\'(x0)', 'Xi', 'Error'])

            while True:
                iteracion += 1
                f_prima_evaluada = f_prima.subs(x, x_actual)
                f_x_evaluada = f_x.subs(x, x_actual)
                f_prima_prima_evaluada = f_prima_prima.subs(x, x_actual)
                x_anterior = x_actual
                x_actual = newton_modificado.aproximacion(f_x_evaluada, f_prima_evaluada,f_prima_prima_evaluada, x_anterior)
                x_actual = sp.N(x_actual)
                if x_actual == 0:
                    instancia_respuesta.agregar_parrafo(f"El valor calculado de x es 0, en la iteracion #{iteracion}, por lo tanto no se puede realizar el calculo del error acomulado")
                    instancia_respuesta.agregar_fila([iteracion, x_anterior, f_x_evaluada, f_prima_evaluada, f_prima_prima_evaluada, x_actual, "Error no calculado"])
                    instancia_respuesta.agregar_titulo1("Se muestra la tabla de iteraciones")
                    instancia_respuesta.agregar_tabla()
                    resp= instancia_respuesta.obtener_y_limpiar_respuesta()
                    return jsonify(resp), 200
                error_acomulado = errores.error_aproximado_porcentual(x_anterior,x_actual)
                error_acomulado = sp.N(error_acomulado)
                instancia_respuesta.agregar_fila([iteracion, x_anterior, f_x_evaluada, f_prima_evaluada, f_prima_prima_evaluada, x_actual, error_acomulado])
                if(error_acomulado < error_aceptado):
                    break
                #evaluar el criterio de convergencia
                f_prima_evaluada = f_prima.subs(x, x_actual)
                f_prima_prima_evaluada = f_prima_prima.subs(x, x_actual)
                f_x_evaluada = f_x.subs(x, x_actual)
                if f_prima_evaluada == 0:#evaluando que no haya divicion sobre 0
                    print("La derivada evaluada en la raiz es 0")
                    instancia_respuesta.agregar_parrafo(f"La derivada evaluada en la raiz es 0, en la iteracion #{iteracion}, por lo tanto no se puede continuar con el metodo")
                    break
                criterio = abs((f_x_evaluada*f_prima_prima_evaluada)/(f_prima_evaluada**2))
                if criterio > 1:
                    print("El criterio de convergencia no se cumple")
                    resp = instancia_respuesta.responder_error("El criterio de convergencia no se cumple")
                    return jsonify(resp), 400
            
            instancia_respuesta.agregar_titulo1("Resultados")
            instancia_respuesta.agregar_clave_valor("Iteraciones:", iteracion)
            instancia_respuesta.agregar_clave_valor("Raiz:", x_actual)
            instancia_respuesta.agregar_clave_valor("Error:",error_acomulado)
            instancia_respuesta.agregar_tabla()
            resp = instancia_respuesta.obtener_y_limpiar_respuesta()
            return jsonify(resp), 200
        except Exception as e:
            resp = instancia_respuesta.responder_error("Error interno del codigo" + str(e))
            return jsonify(resp), 500




