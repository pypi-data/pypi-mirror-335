"""
Esta es la documentacion de player
"""

class Player:
    """
    Esta clase crea un reproductor de musica
    """

    def play(self, song):

        """

        Este Metodo reproduce la cancion 
        mandada por parametros

        Parameters:
        song (str) : Recibe la cancion a reproducir
        
        Returns:
        int: Devuelve 1 si se reproduce con exito
        """
        print("Reproduciendo cancion", song)
