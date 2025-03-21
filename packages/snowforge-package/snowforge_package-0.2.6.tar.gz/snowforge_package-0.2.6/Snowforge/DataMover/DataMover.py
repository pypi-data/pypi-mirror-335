import os
import multiprocessing as mp


from .Extractors.ExtractorStrategy import ExtractorStrategy
from ..Logging import Debug

class Engine():
    
    def __init__(self):
        """Initialize the DatMover engine. Takes the ExtractStrategy as input (i.e NetezzaExtractor, OracleExtractor etc.)"""

    
    @staticmethod
    def parallel_process(worker_func: object, args_list: list[tuple], num_workers: int = None, use_shared_queue: bool = False, queue = None):
        """
        Executes a worker function 'worker_func' in parallel using a number multiple processes defined by the 'num_workers' variable.

        Args:
            worker_func (function): The function that each worker process should execute.
            args_list (list): A list of tuples, where each tuple contains arguments for worker_func.
            num_workers (int, optional): Number of parallel workers. Defaults to max(4, CPU count - 2).
            use_shared_queue (bool, optional): If True, a multiprocessing queue will be created and passed to workers.
            queue (mp.Queue, optional): If provided, it will be used instead of creating a new queue.

        Returns:
            list: List of results from worker processes if applicable.
        """

        # Determine the number of CPU cores to use
        if num_workers is None:
            num_workers = max(4, os.cpu_count() - 2) #failsafe slik at noen kjerner er tilgjengelig for systemet

        num_processes = min(num_workers, len(args_list))

        process_list = []
        if use_shared_queue and queue is None:
            Debug.log("You HAVE to supply a queue as input to this function if you set 'use_shared_queue = True', otherwise the queue will not be reachable to produces/consumer processes on the other side!", 'WARNING')
            raise SyntaxError

        # Create and start all worker processes
        for i in range(num_processes):

            if use_shared_queue:
                process = mp.Process(target=worker_func, args=(*args_list[i], queue))
            else:
                process = mp.Process(target=worker_func, args=args_list[i])

            process.daemon = True  # Ensure processes exit when main program exits. This ensures no orphans or zombies
            process_list.append(process)
            process.start()

        return process_list  # Return the list of running processes

    
    @staticmethod
    def determine_file_offsets(file_name: str, num_chunks: int):
        """Determine file offsets for parallel reading based on line breaks."""
        file_size = os.path.getsize(file_name)
        chunk_size = max(1, file_size // num_chunks)

        offsets = [0]
        with open(file_name, 'rb') as f:
            for _ in range(num_chunks - 1):
                f.seek(offsets[-1] + chunk_size)
                f.readline()
                offsets.append(f.tell())
        print(f"DEBUG: File offsets computed: {offsets}")
        return offsets
    
    @staticmethod
    def export_to_file(extractor: ExtractorStrategy, output_path: str, fully_qualified_table_name: str, filter_column: str = None, filter_value: str = None, verbose: bool = False):
        """Utilizes the selected Extractor to export database(s) to a csv file."""
        
        csv_file = extractor.export_external_table(output_path, fully_qualified_table_name, filter_column, filter_value, verbose)
        return csv_file
    
    @staticmethod
    def calculate_chunks(external_table: str, compression: int = 2):
        """Calculates how many chunks to split the file into."""
        unzipped_chunk_filesize = 100 * 1024 * 1024 * compression   # 200 MB zipped (added compression_factor in order to account for the compression factor of gzip on table data)
        total_filesize = os.path.getsize(external_table)
        
        if total_filesize > unzipped_chunk_filesize:
            num_chunks = max(4, int(total_filesize // unzipped_chunk_filesize)) # ensures that at least three chunks is created (trekker fra 1 lenger nede i koden)
        else:
            num_chunks = 2

        Debug.log(f"\nTotal filesize: {total_filesize // (1024*1024)} mb\nnumber of chunks: {num_chunks - 1}\n", 'INFO')
        
        return num_chunks