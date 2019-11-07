# -*- coding: utf-8 -*-
"""
Using interpreter version Python 2.7.

This file is intended for completion of the assignment given at:
https://github.com/ActiveWebsite/data_test_develop

Completed by Nick Friedl (friedl2@wisc.edu) November 2019.

This file contains functions used for parsing, manipulating, and writing XML.
See READEME.md for more details. The functions assume a certain structure in
the XML document. Each function has some very basic validation and exception 
handling. The XML should be a root containing children who represent
elements of some kind of data all with the same structure, e.g. with 
"Listings" as the root and each "Listing" as a child:
  <Listings>
    <Listing>
      ...
    </Listing>
    <Listing>
      ...
    </Listing>
    ...
    <Listing>
      ...
    </Listing>
  </Listings>

"""
import xml.etree.ElementTree as ET
from urllib import urlopen
from datetime import datetime
import csv
import sys

class MissingTagError(Exception):
  """Raised when a tag is not found in the XML tree"""
  pass

def writeXMLToCSV(root, fileStr, chosenTags):
  """
  Loop over chlidren in `root` and writes all tags in `chosenTags` from the
  XML document specified by `root` to a CSV file named `fileStr`.

  Parameters
  ----------
  root : xml.etree.ElementTree.Element
    The root of the XML document.
  fileStr : str
    Name of the CSV file to be written to.
  chosenTags : [(str, bool)]
    List of paths from child to element that will be written to CSV. The second
    argument in the tuple represents whether or not the element will be
    aggregated when written to the CSV or not. When True, all elements one level
    below the path will be comma joined into one. When False, only the text of
    the specified element will be written.

  Raises
  -------
  TypeError
    If arguments are not typed as specified
  IOError
    If there are issues opening or closing the file.


  """
  if not isinstance(root, ET.Element) or not isinstance(fileStr, basestring) or \
     not isinstance(chosenTags, list):
    raise TypeError("Invalid argument type.")
  for x in chosenTags:
    if not isinstance(x, tuple) or not isinstance(x[0], basestring) or \
       not isinstance(x[1], bool):
      raise TypeError("Invalid argument type.")
  try:
    csvFile = open(fileStr, "w")
  except IOError:
    raise
  try:
    writer = csv.writer(csvFile, dialect="excel")

    for child in root:
      row = []
      for tag, isAggregate in chosenTags:
        if isAggregate:
          aggregate = ""
          handle = child.find(tag)
          if handle is not None:
            for baby in handle:
              aggregate += baby.text + ","
            aggregate = aggregate[0:-1] # remove last comma
          row.append(aggregate)
        else:
          text = ""
          handle = child.find(tag)
          if handle is not None:
            text = handle.text
          row.append(text)

      writer.writerow(row)
  finally:
    if csvFile is not None:
      try:
        csvFile.close()
      except IOError:
        raise

def sortTree(root, childTag, key):
  """
  Sort the children of the root using the `key` function.

  Parameters
  ----------
  root : xml.etree.ElementTree.Element
    The root of the XML document.
  childTag : str
    The name of the tag of the root's children
  key
    This function takes in an element of the XML document and returns a
    key for comparison (for use with `sorted()`)

  Raises
  -------
  TypeError
    If arguments are not typed as specified

  """
  if not isinstance(root, ET.Element) or not isinstance(childTag, basestring) or \
     not callable(key):
    raise TypeError("Invalid argument type.")
  children = []
  for child in root.findall(childTag):
    children.append(child)
    root.remove(child)

  children = sorted(children, key=key)
  for child in children:
    root.append(child)

def filterTreeByText(root, childTag, path, target):
  """
  Loop over children of the `root` and remove those children whose specified
  tag's text does not contain the `target` string.

  Parameters
  ----------
  root : xml.etree.ElementTree.Element
    The root of the XML document.
  childTag : str
    The name of the tag of the root's children
  path : str
    Path from child to the tag with which to check for target.
  target : str
    A string that an element must contain, otherwise the element will
    be removed.

  Raises
  -------
  TypeError
    If arguments are not typed as specified.
  MissingTagError
    If tag not found on path root/childTag/path.

  """
  if not isinstance(root, ET.Element) or not isinstance(childTag, basestring) or \
     not isinstance(path, basestring) or not isinstance(target, basestring):
    raise TypeError("Invalid argument type.")
  for child in root.findall(childTag):
    tag = child.find(path)
    if tag is None:
      raise MissingTagError("Tag not found in " + childTag + path)
    text = tag.text
    if text is not None:
      text = text.lower()
      if text.find(target.lower()) == -1:
        root.remove(child)

def filterTreeByDate(root, childTag, dtPath, startStr, endStr, dtFormat):
  """
  Loop over children of the `root` and remove those children whose datetime falls
  outside of the specified range. This assumes each child has some tag
  representing a datetime formatted as `dtFormat`.

  Parameters
  ----------
  root : xml.etree.ElementTree.Element
    The root of the XML document.
  childTag : str
    The name of the tag of the root's children
  dtPath : str
    Path from child to the datetime tag with which to be compared.
  startStr : str
    String specifying the lower bound of datetimes (inclusive). Must be of the
    same format as `dtFormat`.
  endStr : str
    String specifying the upper bound of datetimes (exclusive). Must be of the
    same format as `dtFormat`.
  dtFormat : str
    Format string for a datetime as used in ``datetime`` module.

  Raises
  -------
  TyperError
    If arguments are not typed as specified.
  ValueError
    If `startDt`, `endDt`, or any of the childs' datetime is unable to be
    parsed.
  MissingTagError
    If datetime tag not found on path root/childTag/dtPath.

  """
  if not isinstance(root, ET.Element) or not isinstance(childTag, basestring) or \
     not isinstance(dtPath, basestring) or not isinstance(startStr, basestring) or \
     not isinstance(endStr, basestring) or not isinstance(dtFormat, basestring):
    raise TypeError("Invalid argument type.")
  try:
    startDt = datetime.strptime(startStr, dtFormat)
    endDt = datetime.strptime(endStr, dtFormat)
  except ValueError:
    raise

  for child in root.findall(childTag):
    tag = child.find(dtPath)
    if tag is None:
      raise MissingTagError("Tag not found in " + childTag + dtPath)
    try:
      dt = datetime.strptime(tag.text, dtFormat)
    except ValueError:
      raise
    if dt < startDt or dt >= endDt:
      root.remove(child)

def readXMLFromURL(urlStr):
  """
  Parses XML from a given URL and returns the root.

  Parameters
  ----------
  urlStr : str
    A string of a URL
  
  Returns
  -------
  xml.etree.ElementTree.Element
    The root element of the XML document.

  Raises
  ------
  TypeError
    If `urlStr` is not a string.
  IOError
    If urlopen() is unable to open `urlStr`
  xml.etree.ElementTree.ParseError:
    If ET.Element.parse() is unable to parse the document as
    an XML tree.

  """
  if not isinstance(urlStr, basestring):
    raise TypeError("Invalid argument type.")
  try:
    urlHandle = urlopen(urlStr)
  except IOError:
    raise
  try:
    tree = ET.parse(urlHandle)
  except ET.ParseError:
    raise

  return tree.getroot()

def script():
  # Constants for this script.
  childTag = "./Listing"
  dtFormat = "%Y-%m-%d %X" # "datetime" abbreviated as "dt" in variable names here on out.

  try:
    root = readXMLFromURL("http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml") 
  except IOError:
    print "IOError, unable to open URL"
    sys.exit()
  except ET.ParseError:
    print "ParseError, unable to parse document"
    sys.exit()

  filterTreeByDate(root, childTag, "./ListingDetails/DateListed", \
    "2016-01-01 00:00:00", "2017-01-01 00:00:00", dtFormat)

  filterTreeByText(root, childTag, "./BasicDetails/Description", " and ")

  sortTree(root, childTag, 
    lambda x: datetime.strptime(x.find("./ListingDetails/DateListed").text, dtFormat))

  chosenTags = [
    ("./ListingDetails/MlsId", False),
    ("./ListingDetails/MlsName", False),
    ("./ListingDetails/DateListed", False),
    ("./Location/StreetAddress", False),
    ("./ListingDetails/Price", False),
    ("./BasicDetails/Bedrooms", False),
    ("./BasicDetails/FullBathrooms", False),
    ("./BasicDetails/HalfBathrooms", False),
    ("./BasicDetails/ThreeQuarterBathrooms", False),
    ("./RichDetails/Appliances", True),
    ("./RichDetails/Rooms", True),
    ("./BasicDetails/Description", False)
  ]
  try:
    writeXMLToCSV(root, "output.csv", chosenTags)
  except IOError:
    print "IOError, failed to write to CSV"
    sys.exit()

if __name__ == "__main__":
  script()
