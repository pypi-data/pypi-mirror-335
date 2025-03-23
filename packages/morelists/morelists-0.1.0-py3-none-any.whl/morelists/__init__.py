import time

class GameList():
    def __init__(self):
        self.list = {}
        self.flippedList = {}

        self.addValue = 0
        self.subtractValue = 0
        self.multiplyValue = 1
        self.divideValue = 1
        self.sum = 0

    def add(self, item, expires = -1):
        expires += time.time()
        self.list[expires] = {"name":item.get("name", ""), "type":item.get("type", "add"), "value":item.get("value", 0)}
        if self.list[expires]["type"] not in ["add", "subtract", "multiply", "divide"]:
            self.list[expires]["type"] = "add"
        self.flippedList[str(self.list[expires])] = expires

        if item["type"]   == "add":
            self.addValue += item["value"]
        elif item["type"] == "subtract":
            self.subtractValue += item["value"]
        elif item["type"] == "multiply":
            self.multiplyValue += (item["value"] - 1)
        elif item["type"] == "divide":
            self.divideValue += (item["value"] - 1)

    def unsafeAdd(self, item, expires = -1):
        expiration = expires + time.time()
        self.list[expiration] = item
        self.flippedList[str(item)] = expiration
    
        if item["type"]   == "add":
            self.addValue += item["value"]
        elif item["type"] == "subtract":
            self.subtractValue += item["value"]
        elif item["type"] == "multiply":
            self.multiplyValue += (item["value"] - 1)
        elif item["type"] == "divide":
            self.divideValue += (item["value"] - 1)


    def update(self):
        try:
            expiration = min(self.list.keys())
            while expiration < time.time():
                if self.list[expiration]["type"] == "add":
                    self.addValue -= self.list[expiration]["value"]
                elif self.list[expiration]["type"] == "subtract":
                    self.subtractValue -= self.list[expiration]["value"]
                elif self.list[expiration]["type"] == "multiply":
                    self.multiplyValue -= (self.list[expiration]["value"] - 1)
                else:
                    self.divideValue -= (self.list[expiration]["value"] - 1)
                del self.list[expiration]

                expiration = min(self.list.keys())
        except ValueError:
            pass

    def pop(self, name):
        pops = [value for value in self.list.values() if value["name"] == name]
        pops.sort(key=lambda a: a["expires"])
        if pops:
            del self.list[self.flippedList[str(pops[0])]]
            del self.flippedList[str(pops[0])]

    def popAny(self, name):
        pops = [value for value in self.list.values() if value["name"] == name]
        if pops:
            del self.list[self.flippedList[str(pops[0])]]
            del self.flippedList[str(pops[0])]

    def popAll(self, name):
        pops = [value for value in self.list.values() if value["name"] == name]
        if pops:
            for x in range(len(pops)):
                del self.list[self.flippedList[str(pops[x])]]
                del self.flippedList[str(pops[x])]

    def remove(self, item):
        if self.flippedList.get(str(item), None):
            del self.list[self.flippedList[str(item)]]
            del self.flippedList[str(item)]

            if item["type"] == "add":
                self.addValue -= item["value"]
            elif item["type"] == "subtract":
                self.subtractValue -= item["value"]
            elif item["type"] == "multiply":
                self.multiplyValue -= (item["value"] - 1)
            else:
                self.divideValue -= (item["value"] - 1)

    def unsafeRemove(self, item):
        if item in self.list.values():
            del self.list[dict(self.flippedList[str(item)])]
            del self.flippedList[str(item)]

            if item["type"] == "add":
                self.addValue -= item["value"]
            elif item["type"] == "subtract":
                self.subtractValue -= item["value"]
            elif item["type"] == "multiply":
                self.multiplyValue -= (item["value"] - 1)
            else:
                self.divideValue -= (item["value"] - 1)

    def __getattribute__(self, name):
        if name == "sum":
            self.update()
            return (object.__getattribute__(self, "addValue") - 
                    object.__getattribute__(self, "subtractValue")) * \
                   object.__getattribute__(self, "multiplyValue") / \
                   object.__getattribute__(self, "divideValue")
        return object.__getattribute__(self, name)
        







    