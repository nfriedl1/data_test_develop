"""
This tests solution.py

Completed by Nick Friedl (friedl2@wisc.edu) November 2019.

For the sake of time, in these tests I did not worry so much about exceptions
and valid arguments, but more about correct functionality.
"""

import solution as s
import unittest
import logging
import xml.etree.ElementTree as ET

class TestSolution(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    pass

  @classmethod
  def tearDownClass(cls):
    pass

  def setUp(self):
    # No spaces used in xmlStr so as to easily format with .replace()
    xmlStr = """
      <Fruits>
        <Fruit>
          <Type>Banana</Type>
          <Datetime>01_January_1994_9:20</Datetime>
          <Text>One_Hundred_Years_Of_Solitude</Text>
          <Numbers>
            <Number>1</Number>
            <Number>2</Number>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Apple</Type>
          <Datetime>04_July_1776_08:00</Datetime>
          <Text>Love_In_The_Time_Of_Cholera</Text>
          <Numbers>
            <Number>11</Number>
            <Number>12</Number>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Kiwi</Type>
          <Datetime>03_March_1924_12:00</Datetime>
          <Text>The_Autumn_Of_The_Patriarch</Text>
          <Numbers>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Pomegranate</Type>
          <Datetime>06_June_1944_06:30</Datetime>
          <Text>The_General_In_His_Labyrinth</Text>
          <Numbers>
            <Number>101</Number>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Passion_Fruit</Type>
          <Datetime>07_December_1941_07:48</Datetime>
          <Text>News_Of_A_Kidnapping</Text>
          <Numbers>
            <Number>1001</Number>
            <Number>1002</Number>
            <Number>1003</Number>
          </Numbers>
        </Fruit>
      </Fruits>
      """.replace("\n", "").replace(" ", "")

    self.childTag = "./Fruit"
    self.root = ET.fromstring(xmlStr)

    self.logger = logging.getLogger("hi")

  def tearDown(self):
    pass

  def test_readXMLFromURL(self):
    self.assertRaises(IOError, s.readXMLFromURL, "bad url")
    self.assertRaises(ET.ParseError, s.readXMLFromURL, "https://google.com") # not XML

    # Not a great part of this test, as it relies on an external resource:
    testRoot = s.readXMLFromURL("http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml")
    self.assertIsInstance(testRoot, ET.Element)

  def test_filterTreeByDate(self):
    self.assertRaises(s.MissingTagError, s.filterTreeByDate, self.root, self.childTag, "./NotATag", "01_September_1939_00:00", "02_September_1945_23:59", "%d_%B_%Y_%H:%M")
    self.assertRaises(ValueError, s.filterTreeByDate, self.root, self.childTag, "./Datetime", "01_September_1939_00:00", "9/2/1945_23:59", "%d_%B_%Y_%H:%M")

    s.filterTreeByDate(self.root, self.childTag, "./Datetime", "01_September_1939_00:00", "02_September_1945_23:59", "%d_%B_%Y_%H:%M")

    answerStr = """
      <Fruits>
        <Fruit>
          <Type>Pomegranate</Type>
          <Datetime>06_June_1944_06:30</Datetime>
          <Text>The_General_In_His_Labyrinth</Text>
          <Numbers>
            <Number>101</Number>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Passion_Fruit</Type>
          <Datetime>07_December_1941_07:48</Datetime>
          <Text>News_Of_A_Kidnapping</Text>
          <Numbers>
            <Number>1001</Number>
            <Number>1002</Number>
            <Number>1003</Number>
          </Numbers>
        </Fruit>
      </Fruits>
      """.replace("\n", "").replace(" ", "")
    answer = ET.fromstring(answerStr)

    self.assertEqual(ET.tostring(self.root), ET.tostring(answer))


  def test_filterTreeByText(self):
    self.assertRaises(s.MissingTagError, s.filterTreeByText, self.root, self.childTag, "./Flavor", "gross")

    s.filterTreeByText(self.root, self.childTag, "./Text",  "the_")

    answerStr = """
      <Fruits>
        <Fruit>
          <Type>Apple</Type>
          <Datetime>04_July_1776_08:00</Datetime>
          <Text>Love_In_The_Time_Of_Cholera</Text>
          <Numbers>
            <Number>11</Number>
            <Number>12</Number>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Kiwi</Type>
          <Datetime>03_March_1924_12:00</Datetime>
          <Text>The_Autumn_Of_The_Patriarch</Text>
          <Numbers>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Pomegranate</Type>
          <Datetime>06_June_1944_06:30</Datetime>
          <Text>The_General_In_His_Labyrinth</Text>
          <Numbers>
            <Number>101</Number>
          </Numbers>
        </Fruit>
      </Fruits>
      """.replace("\n", "").replace(" ", "")
    answer = ET.fromstring(answerStr)

    self.assertEqual(ET.tostring(self.root), ET.tostring(answer))

  def test_sortTree(self):
    s.sortTree(self.root, self.childTag, lambda x: x.find("./Type").text)

    answerStr = """
      <Fruits>
        <Fruit>
          <Type>Apple</Type>
          <Datetime>04_July_1776_08:00</Datetime>
          <Text>Love_In_The_Time_Of_Cholera</Text>
          <Numbers>
            <Number>11</Number>
            <Number>12</Number>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Banana</Type>
          <Datetime>01_January_1994_9:20</Datetime>
          <Text>One_Hundred_Years_Of_Solitude</Text>
          <Numbers>
            <Number>1</Number>
            <Number>2</Number>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Kiwi</Type>
          <Datetime>03_March_1924_12:00</Datetime>
          <Text>The_Autumn_Of_The_Patriarch</Text>
          <Numbers>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Passion_Fruit</Type>
          <Datetime>07_December_1941_07:48</Datetime>
          <Text>News_Of_A_Kidnapping</Text>
          <Numbers>
            <Number>1001</Number>
            <Number>1002</Number>
            <Number>1003</Number>
          </Numbers>
        </Fruit>
        <Fruit>
          <Type>Pomegranate</Type>
          <Datetime>06_June_1944_06:30</Datetime>
          <Text>The_General_In_His_Labyrinth</Text>
          <Numbers>
            <Number>101</Number>
          </Numbers>
        </Fruit>
      </Fruits>
      """.replace("\n", "").replace(" ", "")
    answer = ET.fromstring(answerStr)

    self.assertEqual(ET.tostring(self.root), ET.tostring(answer))

  def test_writeXMLToCSV(self):
    chosenTags = [("./Type", False), ("./Text", False), ("./Numbers", True)]
    try:
      s.writeXMLToCSV(self.root, "test_output.csv", chosenTags)
    except IOError:
      self.logger.error("Unable to write CSV file")

    answer = '''Banana,One_Hundred_Years_Of_Solitude,"1,2"
      Apple,Love_In_The_Time_Of_Cholera,"11,12"
      Kiwi,The_Autumn_Of_The_Patriarch,
      Pomegranate,The_General_In_His_Labyrinth,101
      Passion_Fruit,News_Of_A_Kidnapping,"1001,1002,1003"
      '''.replace(" ", "")

    try:
      file = open("./test_output.csv", "r")
    except IOError:
      self.logger.error("Unable to open CSV file")

    csvStr = file.read().replace("\r", "")

    self.assertEqual(answer, csvStr)

if __name__ == "__main__":
  unittest.main()
