import fileinput
import sys
from collections import OrderedDict


class DataConverter(object):
  def __init__(self, target_file):
    self.source_files = []
    self.target_file = target_file
  def add_source(self, source_file):
      self.source_files.append(source_file)
    #
  def convert_and_save(self):
    self.convert()
    self.save()
  def get_dict(self, line_data):
      data = OrderedDict()
      data["name"] = line_data[0]
      data["size"] = long(line_data[2]) - long(line_data[1])
      data["strand"] = line_data[3]
      data["commonName"] = line_data[4]
      data["group"] = line_data[5]
      return data
  def convert(self):
      self.data = OrderedDict()
      for source_file in self.source_files:
          with open(source_file) as f:
              self.data[source_file] = []
              for line in f:
                  line_data = line.strip('\r\n').split()
                  if line_data[0] == "chr":
                      continue
                  self.data[source_file].append(self.get_dict(line_data))
  def save(self):
      output_file = open(self.target_file, 'w')
      output_file.write('[\n')
      # for each chromosome in list print sequence to output file
      for file in self.data.keys():
          output_file.write((", ").join([
                self.data_to_string(file, record) for record in self.data[file]
            ]))
      output_file.write(']\n')
      output_file.close()
  def data_to_string(self, source, record):
     return "{\n"+(
        ",\n".join(
            [ "  \"{0}\": \"{1}\"".format(key, record[key]) for key in record.keys() ] + ["  \"{0}\": \"{1}\"".format("source", source),
            "\"imports\": []"] 

        ) )+"\n}"


converter = DataConverter("species.json")
converter.add_source("data/catGenesGroupB2_1corrected.bed")
#converter.add_source("data/catGenesGroupB2_1corrected.bed")
converter.convert_and_save()
