from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


from .models import *


def index(request):
    return render(request, 'vroom/index.html')

@login_required
def entrega(request):
    print(request.POST)
    if(request.POST.get('id')):
        print('post recogido')
        contexto = {
            "id": request.POST.get('id'),
        }
        return render(request, 'vroom/entrega.html', contexto)
    print('NO post recogido')
    return render(request, 'vroom/entrega.html')

@login_required
def dashboard(request):
    return render(request, 'vroom/dashboard.html')

@login_required
def curso(request):
    if (request.POST.get('curso')): 
        id_curso = request.POST.get('curso')

        curso = Curso.objects.get(id = id_curso)

        ejercicios = list(Ejercicio.objects.filter(curso = id_curso).values())
        for ejercicio in ejercicios:
            ejercicio["tipo"] = "ejercicio"
        links = list(Link.objects.filter(curso = id_curso).values())
        for link in links:
            link["tipo"] = "link"
        textos = list(Texto.objects.filter(curso = id_curso).values())
        for texto in textos:
            texto["tipo"] = "texto"
        documentos = list(Documento.objects.filter(curso = id_curso).values())
        for documento in documentos:
            documento["tipo"] = "documento"
        
        contenidos = ejercicios+links+textos+documentos   
        contenidos = sorted(contenidos, key=lambda contenido: contenido.get("fecha_publicacion"))

        rol = Usuario_Curso.objects.get(usuario = request.user.id, curso = id_curso).tipo_subscripcion.nombre

        contexto = {
            "curso": curso,
            "contenidos": contenidos,
            "rol": rol
        }

        return render(request, 'vroom/curso.html', contexto)

from django.forms.models import model_to_dict

@login_required
def ejercicio(request):
    if (request.POST.get('id')):
        ejercicio = Ejercicio.objects.get(id = request.POST.get('id'))

        ejercicio_dict = model_to_dict(ejercicio)
        ejercicio_dict["tipo"] = ejercicio.tipo_ejercicio.nombre
        ejercicio_dict["curso_nombre"]= ejercicio.curso.titulo

        rol = Usuario_Curso.objects.get(usuario = request.user, curso = ejercicio.curso).tipo_subscripcion

        if (rol.nombre == "Alumno"):
            try:
                entrega = (Entrega.objects.filter(ejercicio = ejercicio.id, autor = request.user).values())
                entrega = list(entrega)[0]
                try:
                    profesor = Usuario.objects.get(id = entrega["profesor_id"])
                    entrega["profesor"] = profesor.first_name + " " + profesor.last_name
                except:
                    entrega["profesor"] = False
            except:
                entrega = False

            contexto = {
                "ejercicio": ejercicio_dict,
                "entrega": entrega
            }

            return render(request, 'vroom/ejercicio_alumno.html', contexto)

        else:
            
            alumnos_curso = list(Usuario_Curso.objects.filter(curso = ejercicio.curso, tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Alumno").id).values())

            alumnos = []
            for alumno in alumnos_curso:
                id_alumno = alumno["usuario_id"]
                alumnos.append(model_to_dict(Usuario.objects.get(id = id_alumno)))
                
            contexto = {
                "ejercicio": ejercicio_dict,
                "alumnos": list(alumnos)
            }

            return render(request, 'vroom/ejercicio_profesor.html', contexto)