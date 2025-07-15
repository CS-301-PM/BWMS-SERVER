pragma solidity ^0.8.19;

contract InventoryLedger {
    event RequestApproved(
        uint indexed requestId,
        address indexed requester,
        string itemId,
        uint quantity
    );

    event StockUpdated(
        string indexed itemId,
        uint newQuantity,
        string actionType  // "ADD", "REMOVE", "UPDATE"
    );

    address public admin;

    constructor() {
        admin = msg.sender;
    }

    function logRequestApproval(
        uint requestId,
        string memory itemId,
        uint quantity
    ) external {
        require(msg.sender == admin, "Only admin");
        emit RequestApproved(requestId, tx.origin, itemId, quantity);
    }

    function logStockUpdate(
        string memory itemId,
        uint newQuantity,
        string memory actionType
    ) external {
        require(msg.sender == admin, "Only admin");
        emit StockUpdated(itemId, newQuantity, actionType);
    }
}