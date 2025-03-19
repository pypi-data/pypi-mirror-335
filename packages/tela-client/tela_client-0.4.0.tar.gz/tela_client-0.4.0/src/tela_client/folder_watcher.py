import os
import time
import csv
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .client import TelaClient, file

class FileHandler(FileSystemEventHandler):
    def __init__(self, process_function=None, output_format='csv', log_file='logs/processing.log'):
        self.process_function = process_function if process_function else self.default_process_function
        self.output_format = output_format
        self.log_file = log_file

    def on_created(self, event):
        if not event.is_directory and not event.src_path.endswith(('.csv', '.log', '.processing')):
            self.process_file(event.src_path)

    def process_file(self, file_path):
        file_name = os.path.basename(file_path)
        folder_path = os.path.dirname(file_path)
        processed_folder = os.path.join(folder_path, 'processed')
        output_folder = os.path.join(folder_path, 'results')
        log_folder = os.path.join(folder_path, 'logs')
        error_folder = os.path.join(folder_path, 'errors')

        os.makedirs(processed_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(log_folder, exist_ok=True)
        os.makedirs(error_folder, exist_ok=True)

        processing_file = os.path.join(folder_path, f"{file_name}.processing")
        
        try:
            # Create processing file
            open(processing_file, 'w').close()

            # Log start of processing
            self.log(f"Started processing {file_name}")

            # Process the file
            result = self.process_function(file_path)

            # Save output
            output_file = os.path.join(output_folder, f"{file_name}.{self.output_format}")
            self.save_output(result, output_file)

            # Move original file to processed folder
            os.rename(file_path, os.path.join(processed_folder, file_name))

            # Update summary
            self.update_summary(file_name, result)

            # Log completion
            self.log(f"Finished processing {file_name}")

        except Exception as e:
            self.log(f"Error processing {file_name}: {str(e)}")
            # Move original file to errors folder
            os.rename(file_path, os.path.join(error_folder, file_name))

        finally:
            # Remove processing file
            if os.path.exists(processing_file):
                os.remove(processing_file)

    def default_process_function(self, file_path):
        # Default processing function does nothing
        return {}

    def save_output(self, data, output_file):
        if self.output_format == 'csv':
            with open(output_file, 'w', newline='') as f:
                if isinstance(data, list):
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                elif isinstance(data, dict):
                    writer = csv.DictWriter(f, fieldnames=data.keys())
                    writer.writeheader()
                    writer.writerow(data)
        elif self.output_format == 'txt':
            with open(output_file, 'w') as f:
                f.write(str(data))
        else:  # Default to JSON
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)

    def update_summary(self, file_name, result):
        summary_file = os.path.join(os.path.dirname(self.log_file), 'summary.csv')
        
        if isinstance(result, dict):
            result['file_name'] = file_name
            fieldnames = list(result.keys())
        elif isinstance(result, list) and result:
            result[0]['file_name'] = file_name
            fieldnames = list(result[0].keys())
        else:
            return  # Can't create summary for this type of result

        file_exists = os.path.isfile(summary_file)
        
        with open(summary_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            if isinstance(result, dict):
                writer.writerow(result)
            elif isinstance(result, list):
                writer.writerows(result)

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"{timestamp} - {message}\n")

def watch_folder(folder_path, process_function=None, output_format='csv'):
    log_file = os.path.join(folder_path, 'logs', 'processing.log')
    
    event_handler = FileHandler(process_function, output_format, log_file)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()

    print(f"Watching folder: {folder_path}")
    print("Press Ctrl+C to stop...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def run_canvas_on_folder_update(api_key, folder_path, canvas_id, input_variable, output_format='csv'):
    def canvas_process_function(file_path):
        tela_client = TelaClient(api_key)
        canvas = tela_client.new_canvas(canvas_id)
        result = canvas.run(**{input_variable: file(file_path)})
        return result

    watch_folder(folder_path, canvas_process_function, output_format)


if __name__ == "__main__":
    import argparse
    from tela_client.client import TelaClient, file

    def canvas_process_function(file_path):
        tela_client = TelaClient(api_key)
        canvas = tela_client.new_canvas(canvas_id)
        result = canvas.run(**{input_variable: file(file_path)})
        return result

    parser = argparse.ArgumentParser(description="Watch a folder and process new files with TelaClient")
    parser.add_argument("api_key", help="Your Tela API key")
    parser.add_argument("folder_path", help="Path to the folder to watch")
    parser.add_argument("canvas_id", help="ID of the canvas to use for processing")
    parser.add_argument("input_variable", help="Name of the input variable for the canvas")
    parser.add_argument("--output-format", choices=['csv', 'txt', 'json'], default='csv', help="Output format (default: csv)")

    args = parser.parse_args()

    api_key = args.api_key
    canvas_id = args.canvas_id
    input_variable = args.input_variable

    watch_folder(args.folder_path, canvas_process_function, args.output_format)
