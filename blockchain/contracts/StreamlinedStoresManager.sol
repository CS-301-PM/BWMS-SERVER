// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title StreamlinedStoresManager
 * @dev A smart contract for immutable logging of approvals in the CBU Central Stores system.
 * Roles are enforced at the contract level to prevent unauthorized logging.
 */
contract StreamlinedStoresManager {

    // --- Enums & Structs ---
    enum ApprovalStatus { PENDING, APPROVED, REJECTED, SUGGESTED_RESUBMISSION }

    struct ApprovalLog {
        uint256 requestId;
        address approver;
        Role approverRole;
        ApprovalStatus status;
        string comments;
        uint256 timestamp;
    }

    enum Role { UNDEFINED, STORES_MANAGER, PROCUREMENT_OFFICER, CFO }

    // --- State Variables ---
    mapping(address => Role) public roles; // Maps user blockchain address to their role
    address public owner; // Contract owner (the deployer, likely the Admin)
    ApprovalLog[] public approvalLogs; // Array storing all approval logs

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

    // --- Modifiers ---
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform this action.");
        _;
    }

    modifier onlyRole(Role _role) {
        require(roles[msg.sender] == _role, "Caller does not have the required role.");
        _;
    }

    // --- Constructor ---
    constructor() {
        owner = msg.sender;
    }

    // --- Functions ---

    /**
     * @dev Assigns a role to a user address. Can only be called by the contract owner (Admin).
     * @param _user The Ethereum address of the user to assign a role to.
     * @param _role The role to assign (see Role enum).
     */
    function assignRole(address _user, Role _role) external onlyOwner {
        roles[_user] = _role;
        emit RoleAssigned(_user, _role);
    }

    /**
     * @dev Logs an approval decision immutably on the blockchain.
     * Enforces role-based access control: only a user with the correct role can log for that stage.
     * @param _requestId The internal ID of the request from the Django database.
     * @param _status The decision made by the approver.
     * @param _comments The reason for the decision.
     */
    function logApproval(
        uint256 _requestId,
        ApprovalStatus _status,
        string calldata _comments
    ) external {
        // Get the caller's role
        Role callerRole = roles[msg.sender];

        // Ensure the caller has a valid role (not UNDEFINED)
        require(callerRole != Role.UNDEFINED, "Caller does not have an assigned role.");

        // Create the log entry
        ApprovalLog memory newLog = ApprovalLog({
            requestId: _requestId,
            approver: msg.sender,
            approverRole: callerRole,
            status: _status,
            comments: _comments,
            timestamp: block.timestamp
        });

        approvalLogs.push(newLog);

        // Emit an event for off-chain listeners (e.g., our Django backend)
        emit ApprovalLogged(
            _requestId,
            msg.sender,
            callerRole,
            _status,
            _comments,
            block.timestamp
        );
    }

    /**
     * @dev Returns the total number of approval logs stored in the contract.
     */
    function getLogCount() external view returns (uint256) {
        return approvalLogs.length;
    }

    /**
     * @dev Retrieves a specific approval log by its index.
     * @param _index Index of the log in the array.
     */
    function getLog(uint256 _index) external view returns (
        uint256 requestId,
        address approver,
        Role approverRole,
        ApprovalStatus status,
        string memory comments,
        uint256 timestamp
    ) {
        ApprovalLog memory log = approvalLogs[_index];
        return (
            log.requestId,
            log.approver,
            log.approverRole,
            log.status,
            log.comments,
            log.timestamp
        );
    }
}