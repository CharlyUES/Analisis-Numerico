import sympy as sp
from flask import jsonify
from modelos.extras.Funciones import errores, biseccion, respuesta_json, verificaciones, commprobaciones_json
from modelos.extras.latex import conversla,conversla_html




class medoto_biseccion():

    

    @staticmethod
    def calcular_biseccion(json_data):
                
        x = sp.symbols('x')
        #instancio las respuest json
        instancia_respuesta = respuesta_json()

        #obtengo la funcion de json
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
        if verificaciones.obtener_grado(f_x) != None:#es porq es polinomica sino lo es no importa el grado
            if verificaciones.obtener_grado(f_x) < 1:
                resp = instancia_respuesta.responder_error("La función debe ser de grado 1 o mayor")
                return jsonify(resp), 400

        #Verificar los valores iniciales
        try:
            error_aceptable = float(json_data["tolerancia"])
            x1 = float(json_data["xi"])
            xu = float(json_data["xu"])
        except ValueError as e:
            resp = instancia_respuesta.responder_error(f"Error en los valores iniciales\n {str(e)}")
            return jsonify(resp), 400
        except Exception as e:
            resp = instancia_respuesta.responder_error("Error en los datos ingresados" + str(e))
            return jsonify(resp), 400
            
        try:
            #execpciones comunes
            evaluar_x1 = f_x.subs(x,x1)
            evaluar_xu = f_x.subs(x,xu)
            if verificaciones.es_complejo(evaluar_x1) or verificaciones.es_complejo(evaluar_xu):
                resp = instancia_respuesta.responder_error("Los valores iniciales deben de ser reales y validos")
                return jsonify(resp), 400
            if (evaluar_x1 * evaluar_xu) > 0:#no ahy un cambio de signo
                resp = instancia_respuesta.responder_error("No se encontró cambio de signo en los valores iniciales por ende no hay raíz en el intervalo dado")
                return jsonify(resp), 400
        
            condicion = ""
            iteracion =0
            xr = 0
            valor_anterior = xr
            error_acumulado = 100

            instancia_respuesta.crear_tabla()
            instancia_respuesta.agregar_titulo1("Valores Iniciales")
            fx1 = conversla_html.mathl_(f_x)
            instancia_respuesta.agregar_parrafo(f"Funcion: {fx1}")
            instancia_respuesta.agregar_clave_valor("Xi:",x1)
            instancia_respuesta.agregar_clave_valor("Xu:",xu)
            instancia_respuesta.agregar_clave_valor("Tolerancia:",error_aceptable)
            instancia_respuesta.agregar_fila(['Iteracion','X1','Xu','Xr','f(Xr)','Condicion','Error'])
            instancia_respuesta.agregar_titulo1("El calculo de la raiz se hace por la siguiente formula: ")
            html_content = f"""<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>X</mi><mi>r</mi><mo>=</mo><mfrac><mrow><mi>X</mi><mi>i</mi><mo>+</mo><mi>X</mi><mi>u</mi></mrow><mn>2</mn></mfrac></math>"""
            instancia_respuesta.agregar_parrafo(f"Formula: {html_content}")
            html_content = f"""<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>X</mi><mi>r</mi><mo>=</mo><mfrac><mrow><mi>{x1}</mi><mo>+</mo><mi>{xu}</mi></mrow><mn>2</mn></mfrac></math>"""
            instancia_respuesta.agregar_parrafo(f"Iteracion 1: {html_content} = {biseccion.primera_aproximacion(x1,xu)}")
            instancia_respuesta.agregar_parrafo(f"Evaluar f(Xr) = {f_x.subs(x,biseccion.primera_aproximacion(x1,xu))}")
            while True:
                #primera aproximacion
                iteracion +=1
                valor_anterior = xr
                xr = biseccion.primera_aproximacion(x1,xu)
                xr = sp.N(xr)
                evaluacion = biseccion.multiplicacion_evaluadas(f_x,x1,xr)
                if evaluacion > 0:
                    x1 = xr
                    condicion=">0"
                elif evaluacion < 0:
                    xu = xr
                    condicion="<0"
                else:
                    xr = xr #esta es la raiz
                    condicion="=0"
                    error_acumulado = 0
                    instancia_respuesta.agregar_fila([iteracion,x1,xu,xr,evaluacion,condicion,error_acumulado])
                    break
                if not iteracion == 1:
                    if xr == 0:
                        instancia_respuesta.agregar_parrafo(f"El valor calculado de x es 0, en la iteracion #{iteracion}, por lo tanto no se puede realizar el calculo del error acomulado")
                        instancia_respuesta.agregar_fila([iteracion,x1,xu,xr,evaluacion,condicion,"No se puede calcular"])
                        instancia_respuesta.agregar_titulo1("Se muestra la tabla de iteraciones")
                        instancia_respuesta.agregar_tabla()
                        resp= instancia_respuesta.obtener_y_limpiar_respuesta()
                        return jsonify(resp), 200
                    error_acumulado = errores.error_aproximado_porcentual(valor_anterior,xr)
                    error_acumulado = sp.N(error_acumulado)
                    if error_acumulado < error_aceptable:
                        instancia_respuesta.agregar_fila([iteracion,x1,xu,xr,evaluacion,condicion,error_acumulado])
                        break
                instancia_respuesta.agregar_fila([iteracion,x1,xu,xr,evaluacion,condicion,error_acumulado])

            instancia_respuesta.agregar_titulo1("Resultados")
            instancia_respuesta.agregar_clave_valor("Iteraciones:", iteracion)
            instancia_respuesta.agregar_clave_valor("Raiz:",xr)
            instancia_respuesta.agregar_clave_valor("Error:",error_acumulado)
            instancia_respuesta.agregar_tabla()
            resp = instancia_respuesta.obtener_y_limpiar_respuesta()
            return jsonify(resp), 200
        
        except Exception as e:
            resp = instancia_respuesta.responder_error(f"Error interno del codigo:\n {str(e)}")
            return jsonify(resp), 500
        