import pytest
from fortune_teller.fortune_stories import fortune_story
#import Fortune_story



class Tests:
    @pytest.fixture
    def sample_name(self):
            return "Alice"
    
    def test_True(self):
        "verify that a test that always passes"
        expected = True
        result = True
        assert expected == result, "Should always be true"
    def test_return_length(self,sample_name):
        "verify that Fortune_story returns 1 story and not multiple"

        result = fortune_story(sample_name) 
        assert isinstance(result,str), "Should return  a result from our list instead"
        #assert len(result)== 1, "Should contain 1 story from our list"
    

    def test_name_story(self,sample_name):
        "Verify the sample_name is within the story "
        result= fortune_story(sample_name)
        assert sample_name in result , f"the story should contain the inputted name {result}"
    
    def test_valid_story(self,sample_name):
        "What is returned should be within our list of stories"
        valid_stories= [
         f"{sample_name} will wake up one day to find out that his body was taken over by AI. When {sample_name} thought of something, {sample_name}'s body would code it in an instance, but no matter what {sample_name} did, there were always bugs...",
        f"The universe will open and {sample_name} will see the infinte possiblites of error in their code. After looking through millions of possiblites, {sample_name} finally will find the one universe where they will fix their code! Yay!",
        f"While in the ancient Libary, {sample_name} found the ancient text of auto debugger,they opened the book and it read one line: in order to not have bugs one must not code",
        f"{sample_name} will search far and wide in order to find the Grand AI that would save the world. After finding it, the world will turn into binary 1s and 0s, and {sample_name} will become the Grand AI...spooky.",
        f"{sample_name} will travel through the broken world filled with AI and robots. {sample_name} will be the last savior of the World while also being the last software engineer..kinda cool ngl.",
        f"{sample_name} will spend many sleepless nights looking for bugs in their code until {sample_name} will finally notice they were the bug in the code..kafkaesque? You bet!",
        f"{sample_name} will fight against the robot empire and beat them by saying the forbidden digit '1'!",
        f"{sample_name} will break their computer by jumoing inside of it to debug their code and will never be seen again..whaaaaaaaat" 
    ]
        result = fortune_story(sample_name)
        assert result in valid_stories,"The returned story should be a valid option"
    def test_all_stories(self,sample_name):
        "Makes sure that all our stories are acceptable"
        stories= [
           f"{sample_name} will wake up one day to find out that their body was taken over by AI. When {sample_name} thought of something, {sample_name}'s body would code it in an instance, but no matter what {sample_name} did, there were always bugs...",
        f"The universe will open and {sample_name} will see the infinte possiblites of error in their code. After looking through millions of possiblites, {sample_name} finally will find the one universe where they will fix their code! Yay!",
        f"While in the ancient Libary, {sample_name} found the ancient text of auto debugger,they opened the book and it read one line: in order to not have bugs one must not code",
        f"{sample_name} will search far and wide in order to find the Grand AI that would save the world. After finding it, the world will turn into binary 1s and 0s, and {sample_name} will become the Grand AI...spooky.",
        f"{sample_name} will travel through the broken world filled with AI and robots. {sample_name} will be the last savior of the World while also being the last software engineer..kinda cool ngl.",
        f"{sample_name} will spend many sleepless nights looking for bugs in their code until {sample_name} will finally notice they were the bug in the code..kafkaesque? You bet!",
        f"{sample_name} will fight against the robot empire and beat them by saying the forbidden digit '1'!",
        f"{sample_name} will break their computer by jumoing inside of it to debug their code and will never be seen again..whaaaaaaaat" 
    ]
        for i in range(50):
            result = fortune_story(sample_name)
            assert(result in stories),f"Expected to story to be returned from stories instead it returned{result}"