class Veicolo:
    def __init__(self, marca, modello, anno, prezzo):
        self.marca = marca
        self._modello = modello
        self.__anno = anno
        self.prezzo = prezzo
    
    def descrizione(self):
        return f"{self.marca} {self._modello}, Anno: {self.__anno}, Prezzo: {self.prezzo} EUR"
    
    def set_anno(self, anno):
        if isinstance(anno, int) and anno > 1885:
            self.__anno = anno
        else:
            raise ValueError("Anno non valido.")
    
    def get_anno(self):
        return self.__anno
    
    def sconto(self, percentuale):
        if 0 <= percentuale <= 100:
            self.prezzo -= self.prezzo * (percentuale / 100)
        else:
            raise ValueError("Percentuale di sconto non valida.")

class Auto(Veicolo):
    def __init__(self, marca, modello, anno, prezzo, porte):
        super().__init__(marca, modello, anno, prezzo)
        self.porte = porte
    
    def descrizione(self):
        return f"{self.marca} {self._modello}, Anno: {self.get_anno()}, Porte: {self.porte}, Prezzo: {self.prezzo} EUR"
