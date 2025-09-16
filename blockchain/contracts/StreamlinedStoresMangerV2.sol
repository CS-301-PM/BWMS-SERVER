// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title StreamlinedStoresManagerV2
 * @dev A smart contract for immutable logging of key events in the CBU Central Stores system.
 * This is an expanded version supporting Approvals, Deliveries, Relocations, and Damage Reports.
 */
contract StreamlinedStoresManagerV2 {

    // --- Enums & Structs ---
    enum Role { UNDEFINED, STORES_MANAGER, PROCUREMENT_OFFICER, CFO, DEAN, ADMIN }
    enum ApprovalStatus { PENDING, APPROVED, REJECTED, SUGGESTED_RESUBMISSION }
    enum DamageSeverity { LOW, MEDIUM, HIGH, CRITICAL }

    struct ApprovalLog {
        uint256 requestId;
        address approver;
        Role approverRole;
        ApprovalStatus status;
        string comments;
        uint256 timestamp;
    }

    struct DeliveryLog {
        uint256 requestId;
        address deliveredBy;
        string trackingData; // e.g., GRN Number, Supplier Details
        uint256 timestamp;
    }

    struct RelocationLog {
        uint256 itemId;
        address relocatedBy;
        string fromLocation;
        string toLocation;
        uint256 timestamp;
    }

    struct DamageReportLog {
        uint256 itemId;
        address reportedBy;
        DamageSeverity severity;
        string details;
        uint256 timestamp;
    }

    // --- State Variables ---
    mapping(address => Role) public roles;
    address public owner;

    // Arrays for storing all logs
    ApprovalLog[] public approvalLogs;
    DeliveryLog[] public deliveryLogs;
    RelocationLog[] public relocationLogs;
    DamageReportLog[] public damageReportLogs;

    // --- Events ---
    event RoleAssigned(address indexed user, Role role);
    event ApprovalLogged(
        uint256 indexed requestId,
        address indexed approver,
        Role approverRole,
        ApprovalStatus status,
        string comments,
        uint256 timestamp
    );
    event DeliveryLogged(
        uint256 indexed requestId,
        address indexed deliveredBy,
        string trackingData,
        uint256 timestamp
    );
    event RelocationLogged(
        uint256 indexed itemId,
        address indexed relocatedBy,
        string fromLocation,
        string toLocation,
        uint256 timestamp
    );
    event DamageReportLogged(
        uint256 indexed itemId,
        address indexed reportedBy,
        DamageSeverity severity,
        string details,
        uint256 timestamp
    );

    // --- Modifiers ---
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform this action.");
        _;
    }

    modifier hasRole(Role _role) {
        require(roles[msg.sender] == _role, "Caller does not have the required role.");
        _;
    }

    // --- Constructor ---
    constructor() {
        owner = msg.sender;
    }

    // --- Role Management ---
    function assignRole(address _user, Role _role) external onlyOwner {
        roles[_user] = _role;
        emit RoleAssigned(_user, _role);
    }

    // --- Core Logging Functions ---

    function logApproval(
        uint256 _requestId,
        ApprovalStatus _status,
        string calldata _comments
    ) external hasRole(Role.STORES_MANAGER) { // Example: Only Stores Manager can log approvals
        ApprovalLog memory newLog = ApprovalLog({
            requestId: _requestId,
            approver: msg.sender,
            approverRole: roles[msg.sender],
            status: _status,
            comments: _comments,
            timestamp: block.timestamp
        });
        approvalLogs.push(newLog);
        emit ApprovalLogged(_requestId, msg.sender, roles[msg.sender], _status, _comments, block.timestamp);
    }

    function logDelivery(
        uint256 _requestId,
        string calldata _trackingData
    ) external hasRole(Role.PROCUREMENT_OFFICER) { // Example: Only Procurement can log deliveries
        DeliveryLog memory newLog = DeliveryLog({
            requestId: _requestId,
            deliveredBy: msg.sender,
            trackingData: _trackingData,
            timestamp: block.timestamp
        });
        deliveryLogs.push(newLog);
        emit DeliveryLogged(_requestId, msg.sender, _trackingData, block.timestamp);
    }

    function logRelocation(
        uint256 _itemId,
        string calldata _fromLocation,
        string calldata _toLocation
    ) external hasRole(Role.STORES_MANAGER) {
        RelocationLog memory newLog = RelocationLog({
            itemId: _itemId,
            relocatedBy: msg.sender,
            fromLocation: _fromLocation,
            toLocation: _toLocation,
            timestamp: block.timestamp
        });
        relocationLogs.push(newLog);
        emit RelocationLogged(_itemId, msg.sender, _fromLocation, _toLocation, block.timestamp);
    }

    function reportDamage(
        uint256 _itemId,
        DamageSeverity _severity,
        string calldata _details
    ) external {
        // Anyone with a role (not UNDEFINED) can report damage
        require(roles[msg.sender] != Role.UNDEFINED, "Caller does not have an assigned role.");
        DamageReportLog memory newLog = DamageReportLog({
            itemId: _itemId,
            reportedBy: msg.sender,
            severity: _severity,
            details: _details,
            timestamp: block.timestamp
        });
        damageReportLogs.push(newLog);
        emit DamageReportLogged(_itemId, msg.sender, _severity, _details, block.timestamp);
    }

    // --- Getter Functions (Optional, for off-chain querying) ---
    function getApprovalLogCount() external view returns (uint256) { return approvalLogs.length; }
    function getDeliveryLogCount() external view returns (uint256) { return deliveryLogs.length; }
    function getRelocationLogCount() external view returns (uint256) { return relocationLogs.length; }
    function getDamageReportLogCount() external view returns (uint256) { return damageReportLogs.length; }
}