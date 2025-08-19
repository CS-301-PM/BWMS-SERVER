// blockchain/contracts/InventoryLedger.sol
pragma solidity ^0.8.28;

contract InventoryLedger {
    enum ActionType { 
        REQUEST, 
        APPROVAL, 
        REJECTION, 
        STOCK_UPDATE,
        STOCK_MOVEMENT,
        DAMAGE_REPORT,
        DELIVERY_RECORD
        }
    
    struct LogEntry {
        address user;
        uint256 itemId;
        uint256 quantity;
        ActionType action;
        uint256 timestamp;
    }
    
    LogEntry[] public logs;
    address public admin;

    constructor() {
        admin = msg.sender;
    }

    function logAction(
        uint256 itemId,
        uint256 quantity,
        ActionType action
    ) external {
        require(msg.sender == admin, "Only admin can log");
        logs.push(LogEntry(
            msg.sender,
            itemId,
            quantity,
            action,
            block.timestamp
        ));
    }

    function getLogCount() external view returns (uint256) {
        return logs.length;
    }
}