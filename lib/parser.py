import datetime
import os
import shutil
import uuid
import zipfile

import pandas as pd
import lxml.etree as et


def parse(creator, filename):
    """
    Command to load excel file and transform it to series of xml files
    :param creator: fullname of creator
    :param out: output directory
    :param path_to_xls_file: path to excel file
    :return:
    """
    # Open excel file and skips first row
    xls = pd.read_excel('files/'+filename, sheet_name=0, index_col=0, skiprows=1)

    # Checks output directory exists if not creates it
    dirname = filename.replace('.xlsx', '')
    if not os.path.exists('files/'+dirname):
        os.makedirs('files/'+dirname)

    # Iterates excel file and passes row to cmdi element
    for index, row in xls.iterrows():
        if 'http://' not in row['resourceName']:
            cmdi('files/'+dirname+'/', creator, row)

    zipf = zipfile.ZipFile('files/'+dirname+'.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('files/'+dirname, zipf)
    zipf.close()

    remove_file('files/'+filename)
    shutil.rmtree('files/'+dirname, ignore_errors=True)


def remove_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("The file does not exist")


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def cmdi(out, creator, row):
    """
    Creates root element CMDI
    :param out: out directory
    :param creator: fullname of creator
    :param row: row form xls file
    :return:
    """
    NSMAP = {
              None: 'http://www.clarin.eu/cmd/',
              "xsi": 'http://www.w3.org/2001/XMLSchema-instance',
             }

    attr_qname = et.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")

    cmd = et.Element("CMD",
                     {attr_qname: "http://www.clarin.eu/cmd/ https://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/1.1/profiles/clarin.eu:cr1:p_1487686159252/xsd"},
                     nsmap=NSMAP)
    cmd.set("CMDVersion", "1.1")

    resource_id = "res_"+str(uuid.uuid4())
    cmd.append(headers(creator))
    cmd.append(resources(resource_id))
    cmd.append(components([component_text_basic_information(row, resource_id)]))

    tree = et.ElementTree(cmd)
    filename = out+'/'+row['resourceName']+'.xml'
    tree.write(filename, pretty_print=True, xml_declaration=True, encoding="utf-8")


def headers(creator):
    """
    Creates Header element
    :param creator: fullname of creator
    :return: Element
    """
    header = et.Element("Header")
    et.SubElement(header, "MdCreator").text = creator
    et.SubElement(header, "MdCreationDate").text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    et.SubElement(header, "MdProfile").text = "https://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/1.1/profiles/clarin.eu:cr1:p_1487686159252/xsd"
    return header


def resources(resource_id):
    """
    Creates Resource element
    :param resource_id: resource identifier
    :return: Element
    """
    resource = et.Element("Resource")
    resource_proxy_list = et.SubElement(resource, "ResourceProxyList")
    et.SubElement(resource, "JournalFileProxyList")
    et.SubElement(resource, "ResourceRelationList")
    resource_proxy = et.SubElement(resource_proxy_list, "ResourceProxy")
    resource_proxy.set("id", resource_id)
    resource_type = et.SubElement(resource_proxy, "ResourceType")
    resource_type.text = "Resource"
    resource_type.set("mimetype", "text/plain")
    resource_ref = et.SubElement(resource_proxy, "ResourceRef")
    resource_ref.text = ""
    return resource


def components(comp):
    """
    Creates component Element
    :param comp: Component to append
    :return: Element
    """
    component = et.Element("Components")
    for c in comp:
        component.append(c)
    return component


def component_text_basic_information(row, resource_id):
    """
    Creates TextBasicInformation Element
    :param row: Row from excel file
    :param resource_id: resource identifier
    :return: Element
    """
    component = et.Element("TextBasicInformation")
    component.set("ref", resource_id)

    resource_name = et.SubElement(component, "resourceName")
    resource_name.text = check_value(row['resourceName'])
    resource_name.set('{http://www.w3.org/XML/1998/namespace}lang', 'pol')

    text_bibliographic = et.SubElement(component, 'TextBibliographic')
    title = et.SubElement(text_bibliographic, 'title')
    title.text = check_value(row['Title'])
    title.set('{http://www.w3.org/XML/1998/namespace}lang', 'pol')

    et.SubElement(text_bibliographic, 'publicationDate').text = check_value(row['PublicationDate'])
    et.SubElement(text_bibliographic, 'publicationPlace').text = check_value(row['PublicationPlace'])

    authors = et.SubElement(text_bibliographic, 'Authors')
    author = et.SubElement(authors, 'author')
    et.SubElement(author, 'lastName').text = check_value(row['lastName'])
    et.SubElement(author, 'firstName').text = check_value(row['firstName'])
    et.SubElement(author, 'pseudonym').text = check_value(row['pseudonym'])
    et.SubElement(author, 'sex').text = row['sex']

    resource_content = et.SubElement(component, 'ResourceContent')
    genre = et.SubElement(resource_content, 'genre')
    genre.text = check_value(row['Genre'])
    genre.set('{http://www.w3.org/XML/1998/namespace}lang', 'eng')
    et.SubElement(resource_content, 'subject').text = check_value(row['Subject'])
    et.SubElement(resource_content, 'functionalStyle').text = check_value(row['functionalStyle'])
    et.SubElement(resource_content, 'originalSource').text = check_value(row['originalSource'])
    et.SubElement(resource_content, 'keyword').text = check_value(row['keyword'])

    modality_info = et.SubElement(resource_content, 'ModalityInfo')
    et.SubElement(modality_info, 'Modalities').text = check_value(row['Modalities'])
    modality_info.append(descriptions())

    translation = et.SubElement(resource_content, 'Translation')
    et.SubElement(translation, 'translated').text = check_value(row['translated'])
    et.SubElement(translation, 'translatorName').text = check_value(row['translatorName'])
    et.SubElement(translation, 'translationDate').text = check_value(row['translationDate'])

    keys = et.SubElement(resource_content, 'Keys')
    et.SubElement(keys, 'Key').text = check_value(row['Key'])

    resource_content.append(descriptions(check_value(row['Description'])))

    subject_languages = et.SubElement(resource_content, 'SubjectLanguages')
    language = et.SubElement(subject_languages, 'Language')
    language_name = et.SubElement(language, 'LanguageName')
    language_name.text = check_value(row['LanguageName'])
    language_name.set('{http://www.w3.org/XML/1998/namespace}lang', 'eng')
    iso639 = et.SubElement(language, 'ISO639')
    et.SubElement(iso639, 'iso-639-3-code').text = check_value(row['iso-639-3-code'])
    subject_languages.append(descriptions())

    _license = et.SubElement(component, 'License')
    et.SubElement(_license, 'DistributionType').text = row['DistributionType']
    et.SubElement(_license, 'LicenseName').text = check_value(row['LicenseName'])
    et.SubElement(_license, 'LicenseURL').text = check_value(row['LicenseURL'])
    et.SubElement(_license, 'NonCommercialUsageOnly').text = check_value(row['NonCommercialUsageOnly'])
    et.SubElement(_license, 'UsageReportRequired').text = check_value(row['UsageReportRequired'])
    et.SubElement(_license, 'ModificationsRequireRedeposition').text = check_value(row['ModificationsRequireRedeposition'])
    return component


def descriptions(value=''):
    """
    Description Element
    :param value: string value
    :return: Element
    """
    _descriptions = et.Element('Descriptions')
    et.SubElement(_descriptions, 'Description').text = value
    return _descriptions


def check_value(value):
    """
    Checks provided excel cell is not null
    :param value:
    :return:
    """
    if pd.isnull(value):
        return ''
    else:
        return str(value)


