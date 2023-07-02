from  OLXParser import XLSXLoader

url_site = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/lublin/?search%5Bfilter_float_price:from%5D=600"
file = XLSXLoader(url_site)
file.get_data(print_information=True)
file.save_data("offer.xlsx")