# Aubrey Quintana 001044242

import csv
from datetime import timedelta


class HashTable:
    def __init__(self, initial_capacity=40):
        self.table = []
        for i in range(initial_capacity):
            self.table.append([])

    def add(self, key, item):
        # Get the bucket list where the item will go
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        # Update key if already in the bucket
        for key_value in bucket_list:
            if key_value[0] == key:
                key_value[1] = item
                return True

        # If not, add the item to the bucket
        key_value = [key, item]
        bucket_list.append(key_value)
        return True

    def get(self, key):
        key = int(key)
        # Locate the bucket that holds the data
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]
        # Search that bucket for the matching key and return the value
        if self.table[bucket] is not None:
            for key_value in bucket_list:
                if key_value[0] == key:
                    return key_value[1]
        # If key is not found, return None
        return None

    def remove(self, key):
        # Locate the bucket that holds the data
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        # Remove the item from the bucket
        for key_value in bucket_list:
            print(key_value)
            if key_value[0] == key:
                bucket_list.remove([key_value[0], key_value[1]])

    def print(self):
        for item in self.table:
            # Checks cell that contain data
            if item is not None:
                # Prints all data found in cells
                print(item)


class Package:
    def __init__(self, ID, address, city, state, zip_code, deadline, weight, status, delivery_time):
        self.ID = ID
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.status = status
        self.delivery_time = delivery_time

    def __str__(self):
        return "%s, %s, %s, %s, %s, %s, %s, %s" % (self.ID, self.address, self.city, self.zip_code, self.deadline,
                                                   self.weight, self.status, self.delivery_time)


class Truck:
    def __init__(self, capacity, speed, packages, miles, starting_time, name):
        self.capacity = capacity
        self.speed = speed
        self.packages = packages
        self.miles = miles
        self.starting_time = starting_time
        self.driving_time = starting_time
        self.address = 'HUB'
        self.name = name


# Load the information from your package csv file into variables for your hash table
def load_package_data(filename):
    with open(filename) as package:
        package_data = csv.reader(package, delimiter=',')
        next(package_data)
        for package in package_data:
            pID = int(package[0])
            pAddress = package[1]
            pCity = package[2]
            pState = package[3]
            pZip_code = package[4]
            pDeadline = package[5]
            pWeight = int(package[6])
            pStatus = "At the hub"
            pDelivery_time = None

            # Create object that contains all the necessary values
            package_item = Package(pID, pAddress, pCity,
                                   pState, pZip_code, pDeadline, pWeight, pStatus, pDelivery_time)

            # Add the package information into the hash table
            myHash.add(pID, package_item)


# Create an instance of the hash table to call
myHash = HashTable()


# Create empty lists to hold distance and address information
distance_list = []
address_list = []


# read distance csv file into empty distance list
def load_distance_data(filename):
    with open(filename) as distance:
        distance_data = csv.reader(distance, delimiter=',')
        for row in distance_data:
            distance_list.append(row)


# read address csv file into empty address list
def load_address_data(filename):
    with open(filename) as address:
        address_data = csv.reader(address, delimiter=',')
        for row in address_data:
            address_list.append(row[0])


# Call the functions to load the data
load_package_data('package.csv')
load_distance_data('distance.csv')
load_address_data('address.csv')


# find the distance between two addresses
# distance csv is bidirectional so coordinates can be inverted
def distance_between(address1, address2):
    try:
        return float(distance_list[address_list.index(address1)][address_list.index(address2)])
    except:
        return float(distance_list[address_list.index(address2)][address_list.index(address1)])


# need to find the minimum distance between package addresses on the truck,
# so we call the distance between function and return the address with the shortest distance in a loop
def min_distance_from(from_address, truck_packages):
    min_distance = 1000
    next_address = None
    next_ID = 0
    for pID in truck_packages:
        package_item = myHash.get(pID)
        distance = distance_between(from_address, package_item.address)
        if distance <= min_distance:
            min_distance = distance
            next_address = package_item.address
            next_ID = pID
    return next_address, min_distance, next_ID


# truck1 ends delivery at 8:57AM at 2010 W 500 S
# distance_between('2010 W 500 S', 'HUB') = (10.9 miles / 18 mph) * 60 = 36 minutes for truck1 to get back to the hub
# 36-minute drive from 8:57AM = 9:33AM start time for truck 3


# trucks loaded manually, all time constraints accounted for
# packages 3, 38, 36, 18 are all on truck 2
# packages 13, 14, 15, 16, 19, 20 are all delivered together
# packages 6, 25, 28, 32 delayed and don't leave the hub until after 9:05AM
# package 9 address has been updated and not delivered until after 10:20AM
truck1 = Truck(16, 18, [13, 14, 15, 16, 21, 20, 19, 39, 34], 0.0, timedelta(hours=8), 'truck 1')
truck2 = Truck(16, 18, [1, 3, 10, 8, 30, 37, 38,
                        5, 27, 35, 36, 18, 2, 7, 29, 33], 0.0, timedelta(hours=8), 'truck 2')
truck3 = Truck(16, 18, [40, 4, 25, 24, 11, 23, 12, 6,
                        28, 31, 32, 17, 9, 26, 22], 0.0, timedelta(hours=9, minutes=33), 'truck 3')


# algorithm to update delivery of packages on the trucks
# order addresses based on the minimum distance to the next address
# keeps track of updated mileage for each truck
# updates status of package as delivered with delivery time
# after delivery, it removes that package from the truck
# once emptied, the truck returns to the HUB and miles accounted for
def truck_deliver_packages(truck):
    from_address = 'HUB'
    address_visited = ''
    for pID in truck.packages[:]:
        address_visited, distance_traveled, package_ID_delivered = min_distance_from(
            from_address, truck.packages)
        truck.miles += distance_traveled
        truck_traveled_sec = (distance_traveled / truck.speed) * 60 * 60
        truck.driving_time = timedelta(
            seconds=truck_traveled_sec) + truck.driving_time
        package_item = myHash.get(package_ID_delivered)
        package_item.delivery_time = truck.driving_time
        package_item.status = "Delivered by " + truck.name
        from_address = address_visited
        truck.packages.remove(package_ID_delivered)
    back_to_hub = distance_between(address_visited, 'HUB')
    truck.miles = truck.miles + back_to_hub
    return truck.miles


# call the function to deliver the packages off the trucks
truck_deliver_packages(truck1)
truck_deliver_packages(truck2)
truck_deliver_packages(truck3)
total_miles = truck1.miles + truck2.miles + truck3.miles
# print(total_miles) = 108.29 miles


# user interface
if __name__ == '__main__':
    print('What information would you like to see?')

    isExit = True
    while isExit:
        print('1. Print All Package Status and Total Mileage')
        print('2. Get a Single Package Status with ID')
        print('3. Get Package Status with a Time')
        print('4. Exit the Program')
        option = input('Choose an option (1, 2, 3, 4):')
        if option == "1":
            print('Package information:')
            for i in range(len(myHash.table)):
                print('Package: {}'.format(myHash.get(i + 1)))
            print('Total miles traveled:', total_miles)
            print('')
        elif option == "2":
            package_ID = input('Enter a package ID (1-40):')
            print('Package ID:', myHash.get(package_ID).ID, 'Address:', myHash.get(package_ID).address,
                  'Delivered at', myHash.get(package_ID).delivery_time)
            print('')
        elif option == "3":
            user_time = input('What time? (HH:MM:SS)')
            h,m,s = user_time.split(':')
            user_time_obj = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            for i in range(len(myHash.table)):
                package_delivery_time = myHash.get(i+1).delivery_time
                package_ID = myHash.get(i+1).ID
                package_status = myHash.get(i+1).status
                if package_delivery_time <= user_time_obj:
                    print('Package ID:', myHash.get(package_ID).ID, 'Address:', myHash.get(package_ID).address,
                          'Delivered at', myHash.get(package_ID).delivery_time)
                else:
                    if (truck1.name in package_status and truck1.starting_time > user_time_obj) \
                            or (truck2.name in package_status and truck2.starting_time > user_time_obj) \
                            or (truck3.name in package_status and truck3.starting_time > user_time_obj):
                        print('Package ID:', myHash.get(package_ID).ID, 'Address:', myHash.get(package_ID).address,
                              'At the hub')
                    else:
                        print('Package ID:', myHash.get(package_ID).ID, 'Address:', myHash.get(package_ID).address,
                              'Currently en route')
        elif option == "4":
            isExit = False
            print('Have a good day!')

        else:
            print('Wrong option, try again')