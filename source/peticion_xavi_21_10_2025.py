import os
import csv
import glob
import sys
import unicodedata
import shutil
import time

def wait_before_exit(seconds=3):
    """Espera antes de salir - compatible con --noconsole"""
    try:
        input("\nPresiona ENTER para salir...")
    except:
        # Si falla (ej: --noconsole), solo esperar
        time.sleep(seconds)

def remove_accents(text):
    """Elimina tildes y acentos de un texto"""
    # Normaliza el texto a NFD (descompone caracteres acentuados)
    nfd = unicodedata.normalize('NFD', text)
    # Filtra solo los caracteres que no son marcas diacríticas
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

def preprocess_csv(input_file, log_func=print):
    # Obtener el directorio y nombre base del archivo de entrada
    output_dir = os.path.dirname(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    # Crear nombre del archivo de salida agregando '_ok' antes de la extensión
    output_file = os.path.join(output_dir, f"{base_name}_ok.csv")

    # Leer el archivo de entrada y procesarlo
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            reader = csv.reader(infile, delimiter='<')
            writer = csv.writer(outfile, delimiter=';')

            for row in reader:
                # Limpiar cada campo: eliminar punto y coma, "<", ">", y tildes
                cleaned_row = [
                    remove_accents(field.replace(';', '').replace('<', '').replace('>', ''))
                    for field in row
                ]
                writer.writerow(cleaned_row)

        log_func(f"Archivo procesado guardado como: {output_file}")
        return True
    except Exception as e:
        log_func(f"Error procesando {input_file}: {e}")
        return False

# Procesar todos los archivos CSV en el directorio actual
if __name__ == "__main__":
    log_file = None
    try:
        # Obtener el directorio donde se encuentra el script o ejecutable
        # Esto funciona tanto para .py como para .exe compilado con PyInstaller
        if getattr(sys, 'frozen', False):
            # Si está ejecutándose como ejecutable compilado
            current_dir = os.path.dirname(sys.executable)
        else:
            # Si está ejecutándose como script Python
            current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Crear archivo de log
        log_path = os.path.join(current_dir, "proceso_csv.log")
        log_file = open(log_path, 'w', encoding='utf-8')
        
        def log_print(message):
            """Imprime y escribe en el log"""
            print(message)
            if log_file:
                log_file.write(message + "\n")
                log_file.flush()
        
        log_print(f"Directorio de trabajo: {current_dir}\n")
        
        # Crear carpeta de respaldo si no existe
        backup_dir = os.path.join(current_dir, "bck")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            log_print(f"Carpeta de respaldo creada: {backup_dir}")
        
        # Buscar todos los archivos CSV en el directorio
        csv_files = glob.glob(os.path.join(current_dir, "*.csv"))

        if not csv_files:
            log_print("No se encontraron archivos CSV en el directorio.")
            wait_before_exit(5)
            sys.exit(1)

        # Contador de archivos procesados
        processed_count = 0
        
        for csv_file in csv_files:
            # Saltar archivos que ya tienen '_ok' en el nombre para evitar reprocesar
            if not csv_file.endswith('_ok.csv'):
                # Procesar el archivo
                if preprocess_csv(csv_file, log_print):
                    # Si se procesó correctamente, mover el original a la carpeta bck
                    file_name = os.path.basename(csv_file)
                    backup_path = os.path.join(backup_dir, file_name)
                    shutil.move(csv_file, backup_path)
                    log_print(f"Archivo original movido a: {backup_path}")
                    processed_count += 1
        
        log_print(f"\n=== Proceso completado ===")
        log_print(f"Total de archivos procesados: {processed_count}")
        log_print(f"Archivos originales guardados en: {backup_dir}")
        
    except Exception as e:
        import traceback
        error_msg = f"\n!!! ERROR INESPERADO !!!\nTipo de error: {type(e).__name__}\nDetalles: {e}"
        print(error_msg)
        if log_file:
            log_file.write(error_msg + "\n")
            traceback.print_exc(file=log_file)
            log_file.flush()
        traceback.print_exc()
    
    finally:
        # Cerrar archivo de log
        if log_file:
            log_file.write("\n=== Fin del proceso ===\n")
            log_file.close()
        # Pausar al final para que el usuario pueda ver el resultado
        wait_before_exit(5)