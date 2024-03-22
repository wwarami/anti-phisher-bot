from urllib.parse import urlparse

IRANIAN_PSP_LIST = {
    "asan.shaparak.ir": "آسان پرداخت پرشین (آپ)",
    "bpm.shaparak.ir": "به پرداخت ملت",
    "pec.shaparak.ir": "تجارت الکترونیک پارسیان",
    "pecco.shaparak.ir": "تجارت الکترونیک پارسیان",
    "sep.shaparak.ir": "پرداخت الکترونیک سامان",
    "sep2.shaparak.ir": "پرداخت الکترونیک سامان",
    "pep.shaparak.ir": "پرداخت الکترونیک پاسارگاد",
    "pna.shaparak.ir": "پرداخت نوین آرین",
    "sadad.shaparak.ir": "پرداخت الکترونیک سداد",
    "ikc.shaparak.ir": "کارت اعتباری ایران کیش",
    "fanava.shaparak.ir": "فن آوا کارت",
    "fcp.shaparak.ir": "فن آوا کارت",
    "mabna.shaparak.ir": "پرداخت الکترونیک سپهر",
    "pas.shaparak.ir": "(*به پشتیبانی پیام دهید)سایان کارت امید پی",
    "ecd.shaparak.ir": "الکترونیک کارت دماوند",
    "sepehr.shaparak.ir": "پرداخت الکترونیک سپهر"
}


def check_for_https_url(url: str):
    # In this case the better soloutin was requesting the url to check it's ssl 
    #but since the bot will be hosted in a foregin country requesting Iranina payment 
    #gateways won't work!
    # Maybe in future I will solve it using an other api application, but for now...
    return url.startswith('https://')


def check_for_psp(url: str):
    hostname = urlparse(url).hostname 
    if hostname is not None and hostname.startswith("www"):
        hostname = hostname[4:]
        
    psp_provider_name = IRANIAN_PSP_LIST.get(hostname, None)
    if psp_provider_name is None:
        return False
    else:
        return [hostname, psp_provider_name]

