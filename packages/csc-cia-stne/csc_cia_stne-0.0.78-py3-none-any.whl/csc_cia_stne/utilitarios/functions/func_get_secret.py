import os
from botcity.maestro import *
from typing import Optional

def get_secret(name: str, maestro: Optional[BotMaestroSDK] = None) -> str:
        """
        Extrai a secret do ambiente

        Args:
            name (str): nome da variavel ou arquivo da secret
            maestro ( Optional[BotMaestroSDK]): Recebe o Maestro da Botcity. e opcional.

        Returns:
            str: string da secret armazenada na variável de ambiente ou no arquivo de secret
        """
        
        # Tentando extrair da variavel de ambiente
        secret = os.getenv(name)
        
        # secret não encontrada em variavel de ambiente, tentando extrair do arquivo em /secret
        if secret is None:

            # verifica na pasta ./secrets
            if os.path.exists(f"./secrets/{name}"):

                with open(f"./secrets/{name}",'r') as secret_file:
            
                    secret = secret_file.read()

            # verifica na pasta ./.secrets
            elif os.path.exists(f"./.secrets/{name}"):

                with open(f"./.secrets/{name}",'r') as secret_file:
            
                    secret = secret_file.read()

            # verifica na pasta ./private
            elif os.path.exists(f"./private/{name}"):

                with open(f"./private/{name}",'r') as secret_file:
            
                    secret = secret_file.read()

            # verifica na pasta ./.private
            elif os.path.exists(f"./.private/{name}"):

                with open(f"./.private/{name}",'r') as secret_file:
            
                    secret = secret_file.read()

            # verifica na pasta /secrets
            elif os.path.exists(f"/secrets/{name}"):

                with open(f"/secrets/{name}",'r') as secret_file:
            
                    secret = secret_file.read()

            elif maestro and isinstance(maestro, BotMaestroSDK):
                try:
                
                    secret = maestro.get_credential(label=name, key=name)
                
                except Exception as e:
                    
                    secret = None

        return secret