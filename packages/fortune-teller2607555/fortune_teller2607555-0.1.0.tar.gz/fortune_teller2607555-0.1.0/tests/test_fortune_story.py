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
        f"{sample_name} woke up on day to find out that his body was taken over by AI. When he thought of something his body would code it in an instance, but no matter what he did there always bugs",
        f"The universe opens and {sample_name} sees the infinte possiblites of error in his code. After looking through millions of possiblites {sample_name} found the one universe where they fixed their code",
        f"While in the ancient Libary, {sample_name} found the ancient text of auto debugger,they opened the book and it read one line: in order to not have bugs one must not code",
        f"{sample_name} searched far and wide in order to find the Grand AI that would save the world. After finding it the world turned into 1s and 0s and {sample_name} was now the Grand AI",
         f"{sample_name}  travled through the broken world filled with AI and robots they were the last savior of the World they were the last software engineer",
        f"{sample_name} spent many sleepless nights looking for bugs in their code until they noticed they were the bug in the code",
        f"{sample_name} was on a plane flying and it broke apart mid flight, but with their coding skills they hackedd into the world and teleprted to their destinnation",
        f"{sample_name} was on their last leg breathing heavy, but they couldnt give up everyone was counting on {sample_name} and they mereged the pull request",
        f"{sample_name} was fighting against the robot empire and beat them by saying the forbidden digit '1' ",
        f"{sample_name} broke their computer and jumped in to debug their code and was never seen again" 
    ]
        result = fortune_story(sample_name)
        assert result in valid_stories,"The returned story should be a valid option"
    def test_all_stories(self,sample_name):
        "Makes sure that all our stories are acceptable"
        stories= [
        f"{sample_name} woke up on day to find out that his body was taken over by AI. When he thought of something his body would code it in an instance, but no matter what he did there always bugs",
        f"The universe opens and {sample_name} sees the infinte possiblites of error in his code. After looking through millions of possiblites {sample_name} found the one universe where they fixed their code",
        f"While in the ancient Libary, {sample_name} found the ancient text of auto debugger,they opened the book and it read one line: in order to not have bugs one must not code",
        f"{sample_name} searched far and wide in order to find the Grand AI that would save the world. After finding it the world turned into 1s and 0s and {sample_name} was now the Grand AI",
         f"{sample_name}  travled through the broken world filled with AI and robots they were the last savior of the World they were the last software engineer",
        f"{sample_name} spent many sleepless nights looking for bugs in their code until they noticed they were the bug in the code",
        f"{sample_name} was on a plane flying and it broke apart mid flight, but with their coding skills they hackedd into the world and teleprted to their destinnation",
        f"{sample_name} was on their last leg breathing heavy, but they couldnt give up everyone was counting on {sample_name} and they mereged the pull request",
        f"{sample_name} was fighting against the robot empire and beat them by saying the forbidden digit '1' ",
        f"{sample_name} broke their computer and jumped in to debug their code and was never seen again" 
    ]
        for i in range(50):
            result = fortune_story(sample_name)
            assert(result in stories),f"Expected to story to be returned from stories instead it returned{result}"