import fileinput
import sys
from collections import OrderedDict
from operator import itemgetter

class DataConverter(object):
  def __init__(self, target_file):
    self.source_files = []
    self.target_file = target_file
    self.groups = {}
  def add_source(self, source_file, alias):
      self.source_files.append([source_file, alias])
    #
  def convert_and_save(self):
    self.convert()
    self.save()
  def get_dict(self, source_file, alias, line_data):
      data = {}
      data["chr"] = line_data[0]
      data["name"] = "{0}.{1}.{2}.{3}".format(alias, line_data[0], line_data[1], line_data[-2])
      #data["size"] = long(line_data[2]) - long(line_data[1])
      data["start"] = line_data[1]
      #data["strand"] = line_data[3]
      data["commonName"] = line_data[-2]
      data["group"] = line_data[-1]
      if not (data["group"] in self.groups):
          self.groups[data["group"]] = OrderedDict()
      if (not alias in self.groups[data["group"]]):
          self.groups[data["group"]][alias] = data["name"]
      data["file"] = alias
      data["source_file"] = source_file
      data["type"] = alias
      return data
  def convert(self):
      self.data = OrderedDict()
      for [source_file, alias] in self.source_files:
          with open(source_file) as f:
              if not(alias in self.data):
                  self.data[alias] = []
              for line in f:
                  line_data = line.strip('\r\n').split()
                  if line_data[0] == "chr":
                      continue
                  self.data[alias].append(self.get_dict(source_file, alias, line_data))
      for k in self.data.keys():
          self.data[k].sort( key=itemgetter('chr', 'start'))
  def save(self):
      output_file = open(self.target_file, 'w')
      output_file.write('[\n')
      # for each chromosome in list print sequence to output file
      output_file.write(
        (", ").join(
            [
                self.data_to_string(file, record)
                for file in self.data.keys()
                for record in self.data[file]
            ]
            ))
      output_file.write(']\n')
      output_file.close()
  def data_to_string(self, source, record):
      return "{\n"+(
        ",\n".join(
            [ "  \"{0}\": \"{1}\"".format(key, record[key]) for key in record.keys() ] + [
                "  \"imports\": [\n    {0}\n    ]".format(
                    ",\n    ".join([
                        "\"{0}\"".format(
                            value
                            ) for value in self.groups[record["group"]].values()] + [
                                "\"{0}\"".format(record["name"])
                            ]
                        )
                )
            ]
        ) )+"\n}"


converter = DataConverter("species.json")
converter.add_source("data/catGenesGroupB2_1corrected.bed", "cat")
converter.add_source("data/catGenesGroupB2_2corrected.bed", "cat")
converter.add_source("data/cheetahGenesB2corrected.bed", "cheetah")
converter.add_source("data/dogGenesGroup12corrected.bed", "dog")
converter.add_source("data/dogGenesGroup35corrected.bed", "dog")
converter.add_source("data/humanGnesGroup6corrected.bed", "human")

converter.convert_and_save()
