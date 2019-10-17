
"""
Nombre: Alejandro Tejada
Carrera: Ingeniería en Ciencias de la Computación.
Carnet: 17584
Curso: Gráficas por Computadora
Programa: Proyecto2Alejandro.py
Propósito: Este programa es el proyecto hecho en OPENGL
Fecha: 4/5/2019
"""

"""
Zona de librerías
----------------------------------------------------------------------------------------------------------------
"""
import pygame
import random
import numpy
import glm
import pyassimp
import math
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


"""
Inicio del programa principal
"""
# se hace el init para la ventana de pygame
pygame.init()
#la parte del screen y la seteamos con 1000 de ancho con 800 de alto
pantalla = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
#se activa el clock
reloj = pygame.time.Clock()

# hacemos un GlClearColor para tener la pantalla blanca
glClearColor(255,255,255,0.1)
#se habilita la textura y el test
glEnable(GL_DEPTH_TEST)
glEnable(GL_TEXTURE_2D)


"""
Acá inicia el Vertex Shader, este se llama luego y tiene valores de luz y de matrices de modelo, proyección y de la vista
"""
vertex_shader = """
#version 330
layout (location=0) in vec4 PosicionInicial;
layout (location=1) in vec4 normal;
layout (location=2) in vec2 texcoords;

uniform mat4 MatModelo;
uniform mat4 MatView;
uniform mat4 MatProjection;

uniform vec4 color;
uniform vec4 light;

out vec4 vertexColor;
out vec2 vertexTexcoords;

void main()
{
    float Intensidad = dot(normal, normalize(light-PosicionInicial));
    
    gl_Position = MatProjection * MatView * MatModelo * PosicionInicial;

    vertexColor = color * Intensidad;

    vertexTexcoords = texcoords;
}
"""
#inicial el fragment shader, donde se tienen los colores y las coordenadas. 
fragment_shader = """
#version 330
layout (location=0) out vec4 fragColor;
in vec4 vertexColor;
in vec2 vertexTexcoords;
uniform sampler2D tex;

void main()
{
    vec4 textureColor=texture(tex,vertexTexcoords);
    fragColor=vertexColor * textureColor;
}

"""
# se crea el shader con el compileProgram
shader = compileProgram(
    compileShader(vertex_shader, GL_VERTEX_SHADER),
    compileShader(fragment_shader, GL_FRAGMENT_SHADER)
)
# se usa el shader en el programa
glUseProgram(shader)

# creacion de matrices
#creamos la model y la view y la
MatModel = glm.mat4(1)
#creamos la matriz de vista
MatView = glm.mat4(1)
#creamos la matriz de proyeccion
MatProjection = glm.perspective(glm.radians(60), 800/600, 0.1, 1000.0)
#creamos un ViewPort()
glViewport(0, 0, 800, 600)

#Este método es el que se itera en cada vuelta del ciclo y el que recibe parámetros de luz y textura.
def glize(node,VectorLuz,VariableTextura):
    MatModel = node.transformation.astype(numpy.float32)
    #se rea el mesh de los nodos
    for mesh in node.meshes:
        #el material se extra del file y el texture igual
        material = dict(mesh.material.properties.items())
        texture = material['file'][2:]
        #este if sirve para verificar si necesitamos algún cambio de textura, automáticamente cambia la textura según el numero que se presione
        if(VariableTextura==1):
             texture_surface = pygame.image.load('10059_big_ben_v1_diffuse.jpg')
        elif(VariableTextura==2):
             texture_surface = pygame.image.load('Ejercicio8.bmp')
        elif(VariableTextura==3):
             texture_surface = pygame.image.load('texturaNebulosa.jpg')
        elif(VariableTextura==4):
             texture_surface = pygame.image.load('texturaAbstracta.jpg')
        #luego de tener la textura, se importa la data y se colocan valores de altura y ancho
        texture_data = pygame.image.tostring(texture_surface, "RGB", 1)
        width = texture_surface.get_width()
        height = texture_surface.get_height()
        #la textura pasa ahora por el Bind de textura, y el Imaage 2D
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        #finalmente pasa por el mipmap
        glGenerateMipmap(GL_TEXTURE_2D)
        #del total de datos se agregan al vertex de data tres cosas:
        #normales
        #vertices
        #coordenadas de las texturas 
        #todas como float de 32
        vertex_data = numpy.hstack((
            numpy.array(mesh.vertices, dtype=numpy.float32),
            numpy.array(mesh.normals, dtype=numpy.float32),
            numpy.array(mesh.texturecoords[0], dtype=numpy.float32)
        ))
        #en la data de los indices van las faces
        index_data = numpy.hstack((
            numpy.array(mesh.faces, dtype=numpy.int32)
        ))
        #en la data del buffer ahora van el bind de los objetos y el de la data. 
        vertex_buffer_object = glGenVertexArrays(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes,
                     vertex_data, GL_STATIC_DRAW)

        #parámetros necesrios
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 9*4, None)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, False, 9*4, ctypes.c_void_p(3*4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, False, 9*4, ctypes.c_void_p(6*4))
        glEnableVertexAttribArray(2)

        #ahora por cada elemento del buffer, se toman el bind del buffer, y se coloca la data del index de dos formas, en la data del buffer y en el buffer perse
        element_buffer_object = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes,
                     index_data, GL_STATIC_DRAW)

        """
        Zona donde creamos valores importantes para matrices, luz y colores. 
        """
        #se coloca en una mat4 uniforme el valor de las matrices de modelo que viene del Vertex_shader
        glUniformMatrix4fv(
            glGetUniformLocation(shader, "MatModelo"), 1, GL_FALSE,
            MatModel
        )
        #en una mat4 colocamos el MAtView que viene del Vertex_shader. 
        glUniformMatrix4fv(
            glGetUniformLocation(shader, "MatView"), 1, GL_FALSE,
            glm.value_ptr(MatView)
        )
        #colocamos el valor de la mat Projection que viene de la vertex shader
        glUniformMatrix4fv(
            glGetUniformLocation(shader, "MatProjection"), 1, GL_FALSE,
            glm.value_ptr(MatProjection)
        )
        #diffuse contiene el material, este valor es el que coloca el coloe
        diffuse = mesh.material.properties['diffuse']
        #color a su vez usa diffuse y el * es para el resto de argumento
        glUniform4f(
            glGetUniformLocation(shader, "color"),
            *diffuse,
            1
        )
        #light es la luz,se colocó un vector de tres posiciones para manipular la luz en X, z y global
        glUniform4f(
            glGetUniformLocation(shader, "light"),
            VectorLuz.x,0,VectorLuz.y,VectorLuz.z
        )
        #se dibujan los elementos de la escena, se invoca a triangles y al index data
        glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)
    #por cada child o elemeno en el nodo de elementos, se retroalimenta a glize con sus propios parámetros
    for child in node.children:
        glize(child,VectorDeLuz,VariableDeTextura)

#se instancia una cámara en la posicion deseada
camera = glm.vec3(0, 0, 100)

#ESte es el process input, acá es donde se ven los procesos que se ingresen desde el teclado, se usan para rotacion, valores de acercamiento, luz y texturas.
def process_input(anguloX,VectorLuz,VariableTextura,Acercamiento):
    #variable para ver cuántos nos dezplazamos
    desplazamiento=0.06
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                anguloX = anguloX-desplazamiento
                camera.x = Acercamiento*math.cos(anguloX)
                camera.z = Acercamiento*math.sin(anguloX)
            if event.key == pygame.K_RIGHT:
                anguloX = anguloX+desplazamiento
                camera.x = Acercamiento*math.cos(anguloX)
                camera.z = Acercamiento*math.sin(anguloX)
            if event.key == pygame.K_KP1:
                if(VectorLuz.z>=220):
                    VectorLuz.z=220
                else:
                    VectorLuz.z=VectorLuz.z+18
            if event.key == pygame.K_KP2:
                if(VectorLuz.z<=0):
                    VectorLuz.z=0
                else:
                    VectorLuz.z=VectorLuz.z-18
            if event.key == pygame.K_KP_PERIOD:
                VectorLuz=glm.vec3(0,0,0)
            if event.key == pygame.K_KP0:
                VectorLuz=glm.vec3(0,0,200)
            if event.key == pygame.K_UP:
                if(camera.y>=190):
                    camera.y=190
                else:
                    camera.y=camera.y+10
            if event.key == pygame.K_DOWN:
                if(camera.y<=-90):
                    camera.y=-90
                else:
                    camera.y=camera.y-10
            if event.key == pygame.K_w:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            elif event.key == pygame.K_f:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            if event.key == pygame.K_KP3:
                VariableTextura=1
            if event.key == pygame.K_KP4:
                VariableTextura=2
            if event.key == pygame.K_KP5:
                VariableTextura=3
            if event.key == pygame.K_KP6:
                VariableTextura=4
            if event.key == pygame.K_KP7:
                if(Acercamiento>=200):
                    acercamiento=200
                else:   
                    Acercamiento = Acercamiento +10 
                    camera.x = Acercamiento*math.cos(anguloX)
                    camera.z = Acercamiento*math.sin(anguloX)
            if event.key == pygame.K_KP8:
                if(Acercamiento<=25):
                    Acercamiento=25
                else:  
                    Acercamiento = Acercamiento -10
                    camera.x = Acercamiento*math.cos(anguloX)
                    camera.z = Acercamiento*math.sin(anguloX)
    return anguloX, VectorLuz,VariableTextura,Acercamiento

#cargamos la escena
EscenaOBJ = pyassimp.load('BigBenTower.obj')

#variables que usaremos en el ciclo While
AnguloRotacionX = 0
VectorDeLuz=glm.vec3(0,0,200)
Centro = 0
VariableDeTextura=1
Acercamiento=100
while True:
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
    #creamos la matriz de vista
    MatView = glm.lookAt(camera, glm.vec3(0, 40, 0), glm.vec3(0, 1, 0))
    #creamos el glize y le mandamos los parámetros
    glize(EscenaOBJ.rootnode,VectorLuz=VectorDeLuz, VariableTextura=VariableDeTextura)
    #creamos el pygame display
    pygame.display.flip()
    #recursión donde recibimos las mismas variables
    AnguloRotacionX,VectorDeLuz,VariableDeTextura,Acercamiento = process_input(AnguloRotacionX,VectorDeLuz,VariableDeTextura,Acercamiento)
    reloj.tick(15)
