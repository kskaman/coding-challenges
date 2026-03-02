import sys

def compare_files(file1, file2):
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        data1 = f1.read()
        data2 = f2.read()
        
        if data1 == data2:
            print('Files are identical.')
            return
            
        print(f'Files differ\n\n')
        
        
        min_len = min(len(data1), len(data2))
        diff_count = 0
        
        for i in range(min_len):
            if data1[i] != data2[i]:
                
                diff_count += 1
                
                    
        print(f'Total differences: {diff_count} out of {min_len} bytes compared.')

compare_files('test.txt', 'test_decompressed.txt')
