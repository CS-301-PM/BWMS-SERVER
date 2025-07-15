
async function main() {
  const InventoryLedger = await ethers.getContractFactory("InventoryLedger");
  const ledger = await InventoryLedger.deploy();
  await ledger.deployed();
  console.log("Contract deployed to:", ledger.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});