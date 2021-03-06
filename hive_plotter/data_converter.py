import fileinput
import sys
from collections import OrderedDict
from operator import itemgetter

class DataConverter(object):
  def __init__(self, target_file):
    self.source_files = []
    self.target_file = target_file
    self.groups = {}
    self.commonNames = {}
    self.ordering = []
  def add_source(self, source_file, alias, data_sort_flag = True, reverse_order = False):
      self.source_files.append([source_file, alias, data_sort_flag, reverse_order])
  def set_ordering(self, ordering):
      self.ordering = ordering
  def convert_and_save(self):
    self.convert()
    self.save()
  def get_dict(self, source_file, alias, line_data):
      data = {}
      data["chr"] = line_data[0]
      data["name"] = "{0}.{1}.{2}.{3}".format(alias, line_data[0], line_data[1], line_data[-2])
      #data["size"] = long(line_data[2]) - long(line_data[1])
      data["start"] = long(line_data[1])
      #data["strand"] = line_data[3]
      data["commonName"] = line_data[-2]
      if not (data["commonName"] in self.commonNames):
          self.commonNames[data["commonName"]] = OrderedDict()
      if (not alias in self.commonNames[data["commonName"]]):
          self.commonNames[data["commonName"]][alias] = [data["name"]]
      else:
          self.commonNames[data["commonName"]][alias].append(data["name"])
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
      self.data_sort = {}
      for [source_file, alias, data_sort_flag, ordering_flag] in self.source_files:
          with open(source_file) as f:
              if not(alias in self.data):
                  self.data[alias] = OrderedDict()
                  self.data_sort[alias] = [data_sort_flag, ordering_flag]
              for line in f:
                  line_data = line.strip(' \t\r\n').split('\t')
                  if line_data[0] == "chr":
                      continue
                  if not(source_file in self.data[alias]):
                      self.data[alias][source_file] = OrderedDict()
                  if not(line_data[0] in self.data[alias][source_file]):
                      self.data[alias][source_file][line_data[0]] = []
                  self.data[alias][source_file][line_data[0]].append(self.get_dict(source_file, alias, line_data))
      for k in self.data.keys():
          if self.data_sort[k][0]:
              for sf in self.data[k].keys():
                  print(sf)
                  for k2 in self.data[k][sf].keys():
                      order = self.data_sort[k][1]
                      if (k2 in ["chr12", "scaffold145", "scaffold823", "chr35"] or sf in ["data/catGenesGroupB2_2corrected.bed"]):
                          order = not order
                      self.data[k][sf][k2].sort(key = itemgetter('start'), reverse = order)
  def save(self):
      output_file = open(self.target_file, 'w')
      output_file.write('[\n')
      # for each chromosome in list print sequence to output file
      output_file.write(
        (", ").join(
            [
                self.data_to_string(file, record)
                for file in self.ordering
                for sf in (reversed(self.data[file].keys()) if self.data_sort[file][1] and file!= "cat" else self.data[file].keys())
                for chromosome in (reversed(self.data[file][sf].keys()) if self.data_sort[file][1] else self.data[file][sf].keys())
                for record in self.data[file][sf][chromosome]
            ]
            ))
      output_file.write(']\n')
      output_file.close()
  def data_to_string(self, source, record):
      return "{\n"+(
        ",\n".join(
            [ "  \"{0}\": \"{1}\"".format(key, record[key]) for key in record.keys() ] + [
                "  \"gene_links\": [\n    {0}\n    ]".format(
                    ",\n    ".join([
                        "\"{0}\"".format(
                            value
                            ) for value in sum(self.commonNames[record["commonName"]].values(), [])] if record["file"] == "cheetah" else []
                            + [
                                "\"{0}\"".format(record["name"])
                            ]
                        )
                )
            ]
        ) )+"\n}"


converter = DataConverter("species.json")
converter.add_source("data/catGenesGroupB2_1corrected.bed", "cat", True, True)
converter.add_source("data/catGenesGroupB2_2corrected.bed", "cat", True, True)
converter.add_source("data/cheetah_mhc_corrected_map.txt", "cheetah", True, False)
converter.add_source("data/dogGenesGroup12corrected.bed", "dog", True, False)
converter.add_source("data/dogGenesGroup35corrected.bed", "dog")
converter.add_source("data/humanGnesGroup6corrected.bed", "human", True, True)

converter.set_ordering(["human", "cat", "cheetah", "dog"])

converter.convert_and_save()
