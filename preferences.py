import os

class Preferences():

    def __init__(self, fileName):
        self.dirty = True
        self.lines = []
        self.fileName = fileName
        if (os.path.exists(fileName)):
            file = open(fileName, 'r')
            self.lines = file.readlines()
            print(self.lines)
            file.close()
            self.dirty = False

    def getValue(self, propertyName, defaultValue):
        for line in self.lines:
            p = line.find("#")
            if p > -1:
                line = line[0:p] # Remove comment
            arr = line.split("=", 2)
            if len(arr) > 1:
                prop = arr[0].strip()
                if prop == propertyName:
                    value = arr[1].strip()
                    print(f"Found {prop}={value}")
                    return value
         
        print(f"Value not found for {propertyName}. Returning default {defaultValue}")
        return defaultValue
        
    def setValue(self, propertyName, newValue):
        self.dirty = True
        changed = False
        for i in range(len(self.lines)):
            line = self.lines[i]
            p = line.find("#")
            comment = ""
            if p > -1:
                comment = line[p:]
                line = line[0:p] # Remove comment
            arr = line.split("=", 2)
            if len(arr) > 1:
                prop = arr[0].strip()
                if prop == propertyName:
                    value = arr[1].strip()
                    print(f"Found {prop}={value}")
                    self.lines[i] = propertyName + "=" + newValue + comment + "\n"
                    changed = True
                    break
        if not changed:
            self.lines.append(f"{propertyName}={newValue}\n")

    def save(self):
        if self.dirty:
            file = open(self.fileName, 'w')
            print(self.lines)
            file.writelines(self.lines)
            file.close()
            print(f"Configuration {self.fileName} written")
            self.dirty = False
