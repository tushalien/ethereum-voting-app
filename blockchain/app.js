Web3 = require('web3')
fs= require('fs')
web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
//console.lweb3.eth.accounts

code = fs.readFileSync('voting.sol').toString()
console.log(code)
solc = require('solc')
compiledCode = solc.compile(code)
abiDefinition = JSON.parse(compiledCode.contracts[':Voting'].interface)
VotingContract = web3.eth.contract(abiDefinition)
console.log(VotingContract)
byteCode = compiledCode.contracts[':Voting'].bytecode
deployedContract = VotingContract.new(['Rahul Gandhi','Arvind Kejriwal','Narendra Modi'],['Delhi','Delhi','Gujarat'],{data: byteCode, from: web3.eth.accounts[0], gas: 4700000})
console.log(deployedContract)
contractInstance = VotingContract.at(deployedContract.address)

//contractInstance.address
abc= compiledCode.contracts[':Voting'].interface

console.log(contractInstance.address)