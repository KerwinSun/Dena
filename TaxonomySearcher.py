import csv


class TaxonomySearcher:

    def __init__(self):

        taxMap = {}
        file = open('taxonomy-with-ids.en-US.csv', 'r', newline='', encoding="utf-8")
        reader = csv.reader(file)
        taxRows = list(reader)

        for rows in taxRows:
            for categories in rows[1:]:
                taxMap[categories.lower()] = ""
        self.taxList = list(taxMap.keys())

    def searchTaxMap(self, term):
        for item in self.taxList:
            if term in item and len(term) > 2:
                print(term + "- hit")
                return True
        else:
            print(term + "- miss")
            return False



