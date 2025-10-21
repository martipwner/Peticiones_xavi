import os
import csv
import glob
import sys
import unicodedata
import shutil

def remove_accents(text):
    """Elimina tildes y acentos de un texto"""
    # Normaliza el texto a NFD (descompone caracteres acentuados)
    nfd = unicodedata.normalize('NFD', text)
    # Filtra solo los caracteres que no son marcas diacríticas
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

def preprocess_csv(input_file):
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

        print(f"Archivo procesado guardado como: {output_file}")
        return True
    except Exception as e:
        print(f"Error procesando {input_file}: {e}")
        return False

# Procesar todos los archivos CSV en el directorio actual
if __name__ == "__main__":
    # Obtener el directorio donde se encuentra el script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Crear carpeta de respaldo si no existe
    backup_dir = os.path.join(current_dir, "bck")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Carpeta de respaldo creada: {backup_dir}")
    
    # Buscar todos los archivos CSV en el directorio
    csv_files = glob.glob(os.path.join(current_dir, "*.csv"))

    if not csv_files:
        print("No se encontraron archivos CSV en el directorio.")
        sys.exit(1)

    # Contador de archivos procesados
    processed_count = 0
    
    for csv_file in csv_files:
        # Saltar archivos que ya tienen '_ok' en el nombre para evitar reprocesar
        if not csv_file.endswith('_ok.csv'):
            # Procesar el archivo
            if preprocess_csv(csv_file):
                # Si se procesó correctamente, mover el original a la carpeta bck
                file_name = os.path.basename(csv_file)
                backup_path = os.path.join(backup_dir, file_name)
                shutil.move(csv_file, backup_path)
                print(f"Archivo original movido a: {backup_path}")
                processed_count += 1
    
    print(f"\n=== Proceso completado ===")
    print(f"Total de archivos procesados: {processed_count}")
    print(f"Archivos originales guardados en: {backup_dir}")