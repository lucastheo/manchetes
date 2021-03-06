import sys
import json
import os 

sys.path.append('../libs')
from frequencies.lib_query_frequencies import QueryFrequency
import lib_json_utils
import lib_token_str
import lib_json_down_file 

__DATA_NEW__ = '--data-new'
__DATA_ALL__ = '--data'
__URL_NEW__ = '--url-new'
__URL_ALL__ = '--url'
__URL_DATA_NEW__ = '--url-data-new'
__URL_DATA_ALL__ = '--url-data'
__ALL__ = '--all'
__MAX__ = 50    

def get_exec()->dict:
    execute = dict()
    execute[__DATA_NEW__] = data_new
    execute[__DATA_ALL__] = data_all
    execute[__URL_NEW__] = url_new
    execute[__URL_ALL__] = url_all
    execute[__URL_DATA_NEW__] = url_data_new
    execute[__URL_DATA_ALL__] = url_data_all
    execute[__ALL__] = all
    return execute

class PATHS:
    @staticmethod
    def ALL_FATHER()->str:
        return '../data/json_refined/most_cited/'
    @staticmethod
    def ALL()->str:
        return '../data/json_refined/most_cited/all_url_all_data.json'
    @staticmethod
    def BY_DATA_FATHER()->str:
        return '../data/json_refined/most_cited/all_url_by_data/'
    @staticmethod
    def BY_DATA(data:str)->str:
        return '../data/json_refined/most_cited/all_url_by_data/__data__.json'.replace('__data__', data )
    @staticmethod
    def BY_URL_FATHER()->str:
        return '../data/json_refined/most_cited/by_url_all_data/'
    @staticmethod
    def BY_URL(url:str)->str:
        return '../data/json_refined/most_cited/by_url_all_data/__url__.json'.replace('__url__', url.replace(':','-').replace('/','_') )
    @staticmethod
    def BY_URL_BY_DATA_FATHER()->str:
        return '../data/json_refined/most_cited/by_url_by_data/'
    @staticmethod
    def BY_URL_BY_DATA(url:str , data:str )->str:
        return '../data/json_refined/most_cited/by_url_by_data/__url__-__data__.json'.replace('__url__', url.replace(':','-').replace('/','_') ).replace( "__data__" , data )
    

def filter_stop_words(var:dict)->dict:
    out = list()
    for token, frequency in var:
        if lib_token_str.in_stop_word_token( token ) == False:
            out.append( (token , frequency ) )
        if len( out ) >= __MAX__:
            return out
    return out 

def generate_jre(tokens_info:dict , path:str , info:dict ):
    order_token = sorted( tokens_info.items(), key=lambda x: x[1], reverse=True )
    filter_order_token = filter_stop_words( order_token )
    out = lib_json_utils.parse_to_jre_most_cited( filter_order_token , info )
    arq = open( path, 'w')
    arq.write( json.dumps( out ) )
    arq.close()
    #print( json.dumps( out , indent = 4) )

def all( query_frequency:QueryFrequency )->None:
    os.makedirs( PATHS.ALL_FATHER() , exist_ok=True )
    info = {'type':'all' , 'query':{}}
    tokens_info = query_frequency.get_tokens_info()
    generate_jre( tokens_info , PATHS.ALL() , info )

def data( tokens_info_by_data:dict )->None:
    os.makedirs( PATHS.BY_DATA_FATHER() , exist_ok=True )
    var = dict()
    cont = dict()
    for data in tokens_info_by_data.keys():
        real_data = convert_data( data )
        for token in tokens_info_by_data[ data ].keys():
            if real_data not in var.keys():
                var[ real_data ] = dict()
                cont[ real_data ] = dict()
            
            if token in var[ real_data ].keys():
                var[ real_data ][ token ] += tokens_info_by_data[ data ][ token ]
                cont[ real_data ][ token ] += 1
            else:
                var[ real_data ][ token ] = tokens_info_by_data[ data ][ token ]
                cont[ real_data ][ token ] = 1

    for real_data in var.keys():
        for token in var[ real_data ].keys():
            var[ real_data ][ token ] = int( var[ real_data ][ token] / cont[real_data][ token ] )

    for data in var.keys():
        info = {'type':'tokens info by data' , 'query':{'data':data } }
        generate_jre( var[data] , PATHS.BY_DATA( data ) , info )

def url( tokens_info_by_url:dict )->None:
    os.makedirs( PATHS.BY_URL_FATHER() , exist_ok=True )
    for url in tokens_info_by_url.keys():
        info = {'type':'tokens info by url' , 'query':{'url':url } }
        generate_jre( tokens_info_by_url[url] , PATHS.BY_URL( url ) , info )

def url_data( tokens_info_by_url_by_data:dict  )->None:
    os.makedirs( PATHS.BY_URL_BY_DATA_FATHER() , exist_ok=True )
    for url in tokens_info_by_url_by_data.keys():
        for data in tokens_info_by_url_by_data[ url ].keys():
            info = {'type':'tokens info by url and data ' , 'query':{ 'url':url ,'data': data }}
            generate_jre( tokens_info_by_url_by_data[url][data] , PATHS.BY_URL_BY_DATA( url , data) , info )

def data_all( query_frequency:QueryFrequency )->None:
    tokens_info_by_data = query_frequency.get_tokens_info_by_data()
    data( tokens_info_by_data )

def data_new( query_frequency:QueryFrequency )->None:
    tokens_info_by_data = query_frequency.get_tokens_info_by_data_in_data( lib_json_down_file.who_are_new_data() )
    data( tokens_info_by_data )

def url_all( query_frequency:QueryFrequency )->None:
    tokens_info_by_data = query_frequency.get_tokens_info_by_url()    
    url( tokens_info_by_data )

def url_new( query_frequency:QueryFrequency )->None:
    tokens_info_by_data = query_frequency.get_tokens_info_by_url_in_data( lib_json_down_file.who_are_new_url())    
    url( tokens_info_by_data )

def url_data_all( query_frequency:QueryFrequency )->None:
    tokens_info_by_url_by_data = query_frequency.get_tokens_info_by_url_by_data()
    url_data( tokens_info_by_url_by_data )

def url_data_new( query_frequency:QueryFrequency )->None:
    tokens_info_by_url_by_data = query_frequency.get_tokens_info_by_url_by_data_in_url_in_data( lib_json_down_file.who_are_new_by_url_by_data() )
    url_data( tokens_info_by_url_by_data )

def convert_data( date:str ):
    if '-' in date:
        var = date.split('-')
        return f"{var[0]}-{var[1]}-{var[2]}"
    raise Exception("Não foi encontrado \"-\" na data "+ date )

if __name__ == "__main__":
    query_frequency = QueryFrequency()
    execute = get_exec()

    if sys.argv[1] in execute.keys():
        print('[ADD  ] Gerando most_cited' , sys.argv[1])
        execute[ sys.argv[1] ]( query_frequency )
        
    else:
        print('[ERROR] Gerando most_cited, argumento não encontrado' , sys.argv[1])
    

