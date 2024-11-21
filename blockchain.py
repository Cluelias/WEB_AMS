import hashlib
import time
import json

class Block:
    def __init__(self, timestamp, employee_id, attendance_status, previous_hash):
        self.timestamp = timestamp
        self.employee_id = employee_id
        self.attendance_status = attendance_status
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.timestamp}{self.employee_id}{self.attendance_status}{self.previous_hash}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # Create the first block, which has no previous block
        genesis_block = Block(time.time(), "genesis", "init", "0")
        self.chain.append(genesis_block)

    def add_block(self, employee_id, attendance_status):
        # Add a new block with employee attendance info
        last_block = self.chain[-1]
        new_block = Block(time.time(), employee_id, attendance_status, last_block.hash)
        self.chain.append(new_block)

    def get_all_attendance(self):
        # Return a list of all attendance records in the blockchain
        attendance_data = []
        for block in self.chain:
            attendance_data.append({
                "employee_id": block.employee_id,
                "attendance_status": block.attendance_status,
                "timestamp": block.timestamp,
                "hash": block.hash
            })
        return attendance_data

    def is_valid(self):
        # Check if the blockchain is valid (no tampered data)
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True
