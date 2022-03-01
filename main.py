import urllib
import urllib.request as urllib2

file_index = 0
index_file_path = 'output/index.txt'
output_documents_path = 'output/'
write_mode = 'w'
site_index = 121670
base_url = 'https://www.russianfood.com/recipes/recipe.php?rid='

print("start crawler")
with open(index_file_path, write_mode) as index_file:
    while file_index < 100:
        file_index += 1
        site_index += 1
        name = output_documents_path + str(file_index) + '.html'
        try:
            url = base_url + str(site_index)
            print(url)
            urllib.request.urlretrieve(url, name)
            result_string = str(file_index) + ' - ' + url.replace("\n", "") + '\n'
            index_file.write(result_string)
            if file_index == 100:
                index_file.close()
                break
        except:
            continue

print("end crawler")
