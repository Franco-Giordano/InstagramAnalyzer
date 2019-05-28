from InstagramAPI import InstagramAPI
import operator
import getpass

class Analizador:

    def __init__(self, usuario, password):
        self.instagram = Instagram(usuario,password)
        self.usuario = usuario

    def preguntar_por_likes(self, persona):
        i = 0
        for x in self.instagram.get_likes_de_mis_publicaciones():
            if persona in x:
                i+=1
        print("{} te ha dado {} likes en tus publicaciones de instagram".format(persona,i))
    '''
    def dar_unfollowers(self):
        unfollowers = []

        for usuario in self.instagram.get_seguidos():
            if not usuario in self.instagram.get_seguidores():
                unfollowers.append(usuario)

        return unfollowers
        '''

    def dar_unfollowers(self, usuario=None):
        unfollowers = []
        if usuario == None or usuario == "":
            usuario = self.usuario
        id_usuario = self.dar_id(usuario)
        seguidos = self.instagram.hacer_lista_seguidos(id_usuario)
        seguidores = self.instagram.hacer_lista_seguidores(id_usuario)
        
        unfollowers = list(set(seguidos) - set(seguidores))
        return unfollowers

    def dar_fans(self, usuario=None):
        fans = []
        if usuario == None or usuario == "":
            usuario = self.usuario
        id_usuario = self.dar_id(usuario)
        seguidos = self.instagram.hacer_lista_seguidos(id_usuario)
        seguidores = self.instagram.hacer_lista_seguidores(id_usuario)

        fans = list(set(seguidores) - set(seguidos))
        return fans
    
    '''
    def dar_fans(self):
        fans = []

        for usuario in self.instagram.get_seguidores():
            if not usuario in self.instagram.get_seguidos():
                fans.append(usuario)

        return fans
    '''
    def dar_id(self,usuario):
        id_usuario = self.instagram.dar_api().searchUsername(usuario)
        id_usuario = str(self.instagram.dar_api().LastJson['user']['pk'])
        return id_usuario
    '''
    def top_likers(self):
        likes = self.instagram.get_likes_de_mis_publicaciones()
        dicc = {}
        for foto in likes:
            for persona in foto:
                if not persona in dicc:
                    dicc[persona] = 1
                else:
                    dicc[persona] += 1
        
        resultado = sorted(dicc.items(), key=operator.itemgetter(1))
        resultado.reverse()
        return resultado
    '''
    def top_likers(self,usuario=None):
        if usuario == None or usuario == "":
            usuario = self.usuario
        id_usuario = self.dar_id(usuario)
        likes = self.instagram.get_likes_publicaciones(id_usuario)
        dicc = {}
        for foto in likes:
            for persona in foto:
                if not persona in dicc:
                    dicc[persona] = 1
                else:
                    dicc[persona] += 1
        
        resultado = sorted(dicc.items(), key=operator.itemgetter(1))
        resultado.reverse()
        return resultado

    def likes_todas_ultimas_fotos(self,  cantidad, usuario=None):

        if usuario == None or usuario == "":
            usuario = self.usuario

        id_usuario = self.dar_id(usuario)
        ids = self.instagram.ids_de_publicaciones(id_usuario)
        likers = self.instagram.get_likes_publicacion(ids[0])

        for i in range(cantidad-1):
            postas_actuales = []
            likers_actuales = self.instagram.get_likes_publicacion(ids[i+1])
            for liker in likers_actuales:
                if liker in likers:
                    postas_actuales.append(liker)

            likers = postas_actuales
        return postas_actuales

    def sacar_autolikes(self):
        usuario = self.usuario
        id_usuario = self.dar_id(usuario)
        id_medias = self.instagram.ids_de_publicaciones(id_usuario)
        likes = self.instagram.get_likes_publicaciones(id_usuario)
        i=0
        for foto in likes:
            if usuario in foto:
                self.instagram.dar_api().unlike(id_medias[i])
            i+=1
class Instagram:

    def __init__(self, usuario, password):
        self.api = InstagramAPI(usuario, password)
        self.api.login()
        id_usuario = self.api.searchUsername(usuario)
        id_usuario = str(self.api.LastJson['user']['pk'])
        self.seguidores = self.hacer_lista_seguidores(id_usuario)
        self.seguidos = self.hacer_lista_seguidos(id_usuario)
        self.ids_de_mis_publicaciones = self.ids_de_mis_publicaciones() #lista con las ids de todas tus publicaciones en orden de recientes a antiguas
        self.likes_de_mis_publicaciones = self.likes_de_mis_publicaciones() #lista de listas con los usuarios que dieron like. mismo orden anterior
    
    def get_likes_de_mis_publicaciones(self):
        return self.likes_de_mis_publicaciones

    def get_likes_publicacion(self, id_actual):
        likes = []
        info = self.api.getMediaLikers(str(id_actual))
        info = self.api.LastJson
        for usuarios in info["users"]:
            likes.append(usuarios["username"])
        return likes

    def get_likes_publicaciones(self, id_usuario):
        likes_en_fotos = []
        ids = self.ids_de_publicaciones(id_usuario)
        i=1
        for id_actual in ids:
            print(i)
            i+=1
            likes_foto_actual = []
            
            info = self.api.getMediaLikers(str(id_actual))
            info = self.api.LastJson
            for usuarios in info["users"]:
                
                likes_foto_actual.append(usuarios["username"])
            likes_en_fotos.append(likes_foto_actual)
        return likes_en_fotos

    def get_seguidores(self):
        return self.seguidores

    def get_seguidos(self):
        return self.seguidos
    
    def dar_api(self):
        return self.api

    def ids_de_publicaciones(self, id_usuario):
        fotos = []
        next_max_id = True

        while next_max_id:
            # first iteration hack
            if next_max_id is True:
                next_max_id = ''

            _ = self.api.getUserFeed(id_usuario,maxid=next_max_id)
            fotos.extend(self.api.LastJson.get('items',[]))
            next_max_id = self.api.LastJson.get('next_max_id', '')
            
        ids=[]
        for x in fotos:
            ids.append(x["pk"])
        return ids

    def ids_de_mis_publicaciones(self):
        fotos = []
        next_max_id = True

        while next_max_id:
            # first iteration hack
            if next_max_id is True:
                next_max_id = ''

            _ = self.api.getSelfUserFeed(maxid=next_max_id)
            fotos.extend(self.api.LastJson.get('items',[]))
            next_max_id = self.api.LastJson.get('next_max_id', '')
        ids=[]
        for x in fotos:
            ids.append(x["pk"])
        return ids

    def likes_de_mis_publicaciones(self):
        likes_en_fotos = []
        for id_actual in self.ids_de_mis_publicaciones:
            likes_foto_actual = []
            
            info = self.api.getMediaLikers(str(id_actual))
            info = self.api.LastJson
            for usuarios in info["users"]:
                
                likes_foto_actual.append(usuarios["username"])
            likes_en_fotos.append(likes_foto_actual)
        return likes_en_fotos

    def hacer_lista_seguidores(self, id_usuario):
        lista = []
        if __name__ == "__main__":
            api = self.dar_api()

            followers = api.getTotalFollowers(id_usuario) #Esto devuelve una lista de diccionarios con datos de los followers
            for usuario in followers: #recorro cada diccionario y me quedo solo con el username
                lista.append(usuario["username"])
        return lista

    def hacer_lista_seguidos(self, id_usuario):
        lista = []
        if __name__ == "__main__":
            api = self.dar_api()

            followings = api.getTotalFollowings(id_usuario)
            for usuario in followings:
                lista.append(usuario["username"])
        return lista
'''
    def hacer_lista_seguidores(self):
        lista = []
        if __name__ == "__main__":
            api = self.dar_api()
   
            user_id = api.username_id


            followers = api.getTotalFollowers(user_id) #Esto devuelve una lista de diccionarios con datos de los followers
            for usuario in followers: #recorro cada diccionario y me quedo solo con el username
                lista.append(usuario["username"])
        return lista

    def hacer_lista_seguidos(self):
        lista = []
        if __name__ == "__main__":
            api = self.dar_api()
   
            user_id = api.username_id


            followings = api.getTotalFollowings(user_id)
            for usuario in followings:
                lista.append(usuario["username"])
        return lista'''

OPCIONES = """
1 - Encontrar los usuarios que likearon TODAS las ultimas <n> fotos de un usuario dado.
2 - Encontrar unfollowers del usuario dado.
3 - Encontrar fans del usuario dado.
4 - ?
"""

usuario = input("Ingrese nombre de usuario: ")
password = getpass.getpass('Ingrese su password: ')

analizador = Analizador (usuario, password)

while(True):

    print(OPCIONES)
    accion = input("Escoja accion: ")


    if accion == "1":
        user = input("Ingrese usuario: ")
        cantidad = int(input("Ingrese cantidad: "))

        '''while (True):
            persona = input("Ingrese usuario de instagram: ")
            analizador.preguntar_por_likes(persona)'''

        personas = analizador.likes_todas_ultimas_fotos(cantidad,user)
        print(personas)
        print(len(personas))

    if accion == "2":
        print(analizador.dar_unfollowers())

    if accion == "3":
        print(analizador.dar_fans())


