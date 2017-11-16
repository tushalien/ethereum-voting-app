pragma solidity ^0.4.11;

contract Voting {
  
  mapping (bytes32 => uint8) public votesReceived;

  bytes32[] public candidateList;
  mapping (bytes32 => bytes32) public constituencyDict;

  function Voting(bytes32[] candidateNames, bytes32[] constituencies) {
    candidateList = candidateNames;
    for(uint i = 0; i < candidateNames.length; i++) {
      constituencyDict[candidateNames[i]] = constituencies[i];
    }
  }

  function totalVotesFor(bytes32 candidate) returns (uint8,bool) {
    bool validCandidateBool;
    string memory validCandidateString;

    (validCandidateBool,validCandidateString) = validCandidate(candidate);
    if (validCandidateBool == false) return (0,false);
    return (votesReceived[candidate],true);
  }

  function voteForCandidate(bytes32 candidate) returns (bool,string){

    bool validCandidateBool;
    string memory validCandidateString;

    (validCandidateBool,validCandidateString) = validCandidate(candidate);

    if (validCandidateBool == false){
      return (false,validCandidateString);
    }
    votesReceived[candidate] += 1;
    return (true,"success");
  }

  function getCandidateConstituency(bytes32 candidate)returns (bool,bytes32) {

    bytes32 my_null;
    bool validCandidateBool;
    string memory validCandidateString;
     (validCandidateBool,validCandidateString) = validCandidate(candidate);
    if (validCandidateBool == false)
    return (false, my_null);
    return (true,constituencyDict[candidate]);
  }

  function validCandidate(bytes32 candidate) returns (bool,string) {
    for(uint i = 0; i < candidateList.length; i++) {
      if (candidateList[i] == candidate) {
        return (true,"success");
      }
    }
    return (false,"candidate doesnot exist");
  }

  function bytes32ToString(bytes32 x) constant returns (string) {
    bytes memory bytesString = new bytes(32);
    uint charCount = 0;
    for (uint j = 0; j < 32; j++) {
        byte char = byte(bytes32(uint(x) * 2 ** (8 * j)));
        if (char != 0) {
            bytesString[charCount] = char;
            charCount++;
        }
    }
    bytes memory bytesStringTrimmed = new bytes(charCount);
    for (j = 0; j < charCount; j++) {
        bytesStringTrimmed[j] = bytesString[j];
    }
    return string(bytesStringTrimmed);
  }

}