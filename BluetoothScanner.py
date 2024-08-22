import objc
from Foundation import NSObject, NSRunLoop, NSLog, NSTimer
import CoreBluetooth
import CoreFoundation  # Import CoreFoundation to stop the run loop

class BluetoothScanner(NSObject):
    def init(self):
        self = objc.super(BluetoothScanner, self).init()
        if self is None:
            return None
        self.manager = CoreBluetooth.CBCentralManager.alloc().initWithDelegate_queue_(self, None)
        self.target_uuid = None  # Target UUID to search for
        self.found_uuid = False  # Flag to track if the UUID was found
        self.target_peripheral = None  # To store the peripheral with the matching UUID
        self.discovered_uuids = set()  # Set to track discovered UUIDs
        self.peripherals = []  # List to store discovered peripherals
        self.run_loop = NSRunLoop.currentRunLoop()  # Reference to the run loop
        return self

    def setTargetUUID_(self, uuid):
        self.target_uuid = uuid

    def centralManagerDidUpdateState_(self, manager):
        if manager.state() == CoreBluetooth.CBManagerStatePoweredOn:
            NSLog("Bluetooth is powered on. Scanning for devices...")
            self.manager.scanForPeripheralsWithServices_options_(None, None)
            # Start a timer to stop scanning after 25 seconds if no device is found
            NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                25.0, self, 'stopScanning:', None, False
            )
        else:
            NSLog("Bluetooth is not available. Please check your settings.")

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, central, peripheral, advertisementData, RSSI):
        uuid = peripheral.identifier().UUIDString()
        if uuid in self.discovered_uuids:
            return  # Skip logging if UUID has already been discovered

        # Add UUID to the set of discovered UUIDs
        self.discovered_uuids.add(uuid)

        peripheral_name = peripheral.name() or "Unknown"
        self.peripherals.append((uuid, peripheral_name))
        NSLog(f"Discovered device - UUID: {uuid}, Name: {peripheral_name}")

        # Check if the discovered UUID matches the target UUID
        if uuid == self.target_uuid:
            self.found_uuid = True
            self.target_peripheral = peripheral
            NSLog("Matching UUID found! Stopping scan immediately...")
            self.manager.stopScan()  # Stop scanning immediately
            self.displayPeripheralName_(peripheral)  # Display the peripheral name
            self.grantAccess()  # Grant access upon matching the UUID
            self.stopRunLoop()  # Stop the run loop immediately after finding the device

    def displayPeripheralName_(self, peripheral):
        # Fetch the peripheral's name if available
        peripheral_name = peripheral.name() or "Unknown"
        NSLog(f"Device name: {peripheral_name}")
        # Display a message box or any other notification mechanism you prefer
        # Example using a simple log statement:
        print(f"Access Granted to device: {peripheral_name}")

    def stopScanning_(self, timer):
        if not self.found_uuid:
            NSLog("Stopping scan...")
            self.manager.stopScan()
            self.denyAccess()  # Deny access if no matching UUID is found
        self.logDiscoveredPeripherals()
        self.stopRunLoop()

    def logDiscoveredPeripherals(self):
        NSLog("Discovered Peripherals:")
        for uuid, name in self.peripherals:
            NSLog(f"UUID: {uuid}, Name: {name}")

    def stopRunLoop(self):
        # Stop the run loop
        CoreFoundation.CFRunLoopStop(self.run_loop.getCFRunLoop())  # Corrected stopping method

    def grantAccess(self):
        NSLog("Access Granted.")
        # You can use a print statement or a GUI message box here:
        print("Access Granted.")  # Or any other prompt mechanism

    def denyAccess(self):
        NSLog("Access Denied.")
        # You can use a print statement or a GUI message box here:
        print("Access Denied.")  # Or any other prompt mechanism

if __name__ == "__main__":
    # Initialize the scanner
    scanner = BluetoothScanner.alloc().init()

    # Ask the user to input the target UUID
    target_uuid = input("Enter the UUID to search for: ")
    scanner.setTargetUUID_(target_uuid)

    # Start the run loop to begin scanning
    NSRunLoop.currentRunLoop().run()
