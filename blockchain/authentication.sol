pragma solidity ^0.4.11;

contract Voting {
  function Voting(bytes32[] candidateNames, bytes32[] constituencies) {
  }

  function totalVotesFor(bytes32 candidate) returns (uint8,bool) {
  }

  function voteForCandidate(bytes32 candidate) returns (bool,string) {
  }

  function getCandidateConstituency(bytes32 candidate)returns (bool,bytes32) {
  }

  function test() returns (bool,string){
  }

  function validCandidate(bytes32 candidate) returns (bool) {
  }

  function bytes32ToString(bytes32 x) constant returns (string) {
  }
}



contract Authentication {
  Voting public voting;
  
  mapping (bytes32 => bool) public votesAvailable;
  
  bytes32[] public voterList;
  mapping (bytes32 => bytes32) public constituencyDict;


  function Authentication(bytes32[] myList,bytes32[] constituencies, address addr) {
    voterList=myList;

    for(uint i = 0; i < voterList.length; i++) {
      // voterList[i] = myList[i];
      // constituencyDict[voterList[i]]=myList[3+i];
      votesAvailable[voterList[i]] = true;
      constituencyDict[voterList[i]] = constituencies[i];

    }
    voting = Voting(addr);
    // voterList=myVoterList;
  }

  function resetVoters() {
    for(uint i = 0; i < voterList.length; i++) {
      votesAvailable[voterList[i]] = true;
    }
  }

  function isVoterExist(bytes32 voter) returns (bool,string) {
    for(uint i = 0; i < voterList.length; i++) {
      if (voterList[i] == voter) {
        return (true,"success");
      }
    }
    return (false,"voter does not exist");
  }

  function isVoteAvailable(bytes32 voter) returns (bool,string)  {
    if(votesAvailable[voter] == true)
    {
      return (true,"success");
    }
    return (false,"votes not available for the voter");
  }

  function checkConstituency(bytes32 candidate, bytes32 voter) returns (bool, string) {
    bool candidateConstituencyBool;
    bytes32 candidateConstituency;
    (candidateConstituencyBool,candidateConstituency) = voting.getCandidateConstituency(candidate);
    if(candidateConstituencyBool == false)
    return (false,"candidate does not exist.");      
    bool isVoterExistBool;
    string memory isVoterExistString;
    (isVoterExistBool,isVoterExistString) = isVoterExist(voter);
    if(isVoterExistBool == false)
      return (false,"voter does not exist.");      
    if(candidateConstituency == constituencyDict[voter])
      return (true,"undefined");
    return (false,"candidate and voter belong to different constituencies.");
  }

  function isAuthentic(bytes32 candidate, bytes32 voter) returns (bool,string) {
    bool validVoterBool;
    string memory validVoterString;
    (validVoterBool,validVoterString) = validVoter(candidate, voter);
    if(validVoterBool == false)
    {
      return (false,validVoterString);
    }
    votesAvailable[voter] = false;
    return (true,"success");
  }

  function ping()returns (bool){
    return true;
  }


  function validVoter(bytes32 candidate, bytes32 voter) returns (bool,string) {
    bool isVoterExistBool;
    bool isVoteAvailableBool;
    bool checkConstituencyBool;
    string memory isVoterExistString;
    string memory isVoteAvailableString;
    string memory checkConstituencyString;
    (isVoterExistBool,isVoterExistString) = isVoterExist(voter);
    (isVoteAvailableBool,isVoteAvailableString) = isVoteAvailable(voter);
    (checkConstituencyBool, checkConstituencyString) = checkConstituency(candidate,voter);

    if(isVoterExistBool == false)
    {
      return (false,isVoterExistString);
    }

    if(isVoteAvailableBool == false)
    {
      return (false,isVoteAvailableString);
    }

    if(checkConstituencyBool == false)
    {
      return (false,checkConstituencyString);
    }

    return (true,"pika");
    
    
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