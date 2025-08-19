// blockchain/scripts/deploy.js
async function main() {
  const [deployer] = await ethers.getSigners();
  const InventoryLedger = await ethers.getContractFactory("InventoryLedger");
  const ledger = await InventoryLedger.deploy();
  
  console.log("Contract deployed to:", ledger.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });