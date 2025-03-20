import pytest
from unittest.mock import MagicMock
from commitPackage import lazyCommit
    
class Tests:
    #
    # Fixtures - Function to setup and teardown mock database before or after a test function is run.
    #
    @pytest.fixture
    def mock_db(self, mocker):
        """
        A pytest fixture that mocks the MongoDB collection find() method.
        """
        mock_collection = MagicMock()  # Create a mock collection
        mock_data = [
            {"style": "funny", "messages": [
                "Fixed a typo that nobody noticed.",
                "Added a space. Hope this helps."
            ]},
            {"style": "serious", "messages": ["Fix bug", "Refactor code", "Update docs"]}
        ]

        mock_collection.find.return_value = mock_data
        mock_collection.find_one.return_value = {"_id": 222333, "style": "funny", "messages": ["Fixed a typo that nobody noticed.", "Added a space. Hope this helps."]}
        mock_collection.insert_one.return_value = MagicMock(inserted_id="some_id")
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        lazyCommit.commit_collection = mock_collection # Patch lazyCommit.db to return the mock collection

        # Create another mock collection for excuses
        mock_excuses = MagicMock()  
        mock_excuses.find.return_value = [{"excuses": ["I blame it on my partner", "I spilled my coffee"]}]
        mock_excuses.find_one.return_value = {"_id": 123123, "excuses": ["I blame it on my partner", "I spilled my coffee"]}
        mock_excuses.insert_one.return_value = MagicMock(inserted_id="some_id")
        mock_excuses.update_one.return_value = MagicMock(modified_count=1)
        lazyCommit.excuse_collection = mock_excuses

        # Create another mock collection for haikus
        mock_haikus = MagicMock()  
        mock_haikus.find.return_value = [{"haikus": ["My code flows like a river", "Like a setting sun, my code disappeared"]}]
        mock_haikus.find_one.return_value = {"_id": 345345, "haikus": ["My code flows like a river", "Like a setting sun, my code disappeared"]}
        mock_haikus.insert_one.return_value = MagicMock(inserted_id="some_id")
        mock_haikus.update_one.return_value = MagicMock(modified_count=1)
        lazyCommit.haiku_collection = mock_haikus

        yield {"commitMessages": mock_collection, "excuses": mock_excuses, "haikus": mock_haikus}

    # Test functions

#--------------------------------------------------RANDOM COMMIT MESSAGE ---------------------------------------

    def test_random_commit_message_with_data(self, mock_db):
        """
        Test case when commit messages exist in the database.
        """
        result = lazyCommit.random_commit_message()
        assert result in ["Fixed a typo that nobody noticed.", "Added a space. Hope this helps.", "Fix bug", "Refactor code", "Update docs"], \
            f"Expected a valid commit message but got '{result}'"


    def test_random_commit_message_no_data(self, mock_db):
        """
        Test case when no commit messages exist.
        """
        mock_db["commitMessages"].find.return_value = []  # Simulate no commit messages

        result = lazyCommit.random_commit_message()
        assert result == "No commit messages found!", \
            f"Expected 'No commit messages found!' but got '{result}'"


    def test_random_commit_message_aggregates_all_messages(self, mock_db):
        """
        Test case to verify that all commit messages from different styles are aggregated before selection.
        """
        # Run the function multiple times to check if all styles of messages appear
        retrieved_messages = set(lazyCommit.random_commit_message() for i in range(100))

        expected_messages = {
            "Fixed a typo that nobody noticed.",
            "Added a space. Hope this helps.",
            "Fix bug", 
            "Refactor code", 
            "Update docs"
        }

        assert retrieved_messages == expected_messages, (
            f"Expected messages {expected_messages} but got {retrieved_messages}"
        )

#-------------------------------------------GENERATE COMMIT MESSAGE-------------------------------------------

    def test_generate_commit_message_retrieves_correct_style(self, mock_db):
        """
        Test case to ensure that when a user requests a specific style,
        only messages from that style are retrieved.
        """
        # Simulate MongoDB behavior: filter messages by style
        def mock_find(query):
            return [doc for doc in mock_db["commitMessages"].find.return_value if doc["style"] == query.get("style")]

        # Override the default behavior of find() to simulate MongoDB filtering when a user inputs a style query
        mock_db["commitMessages"].find.side_effect = mock_find 

        # Testing style: funny
        result = lazyCommit.generate_commit_message("funny")
        expected_messages = ["Fixed a typo that nobody noticed.", "Added a space. Hope this helps."]
        assert result in expected_messages, (f"Expected a message from 'funny' style but got '{result}'")

        # Testing style: serious
        result_serious = lazyCommit.generate_commit_message("serious")
        expected_serious_messages = ["Fix bug", "Refactor code", "Update docs"]
        assert result_serious in expected_serious_messages, (f"Expected a message from 'serious' style but got '{result_serious}'")

   
    def test_generate_commit_message_no_matching_style(self, mock_db):
        """
        Test case to ensure that when a user requests a style that does not exist,
        the function returns the appropriate message.
        """
        # Simulate MongoDB behavior: filter messages by style
        def mock_find(query):
            return [doc for doc in mock_db["commitMessages"].find.return_value if doc["style"] == query.get("style")]

        # Override the default behavior of find() to simulate MongoDB filtering
        mock_db["commitMessages"].find.side_effect = mock_find 

        # Testing a non-existent style: "nostalgic"
        result = lazyCommit.generate_commit_message("nostalgic")
        expected_message = "No commit messages found for style: nostalgic"

        assert result == expected_message, (f"Expected '{expected_message}' but got '{result}'")
    
    
    def test_generate_commit_message_empty_messages(self, mock_db):
        """
        Test case to ensure that when a style exists but has no messages,
        the function correctly returns the expected message.
        """
        def mock_find(query):
            return [{"style": "empty_style", "messages": []}]  

        mock_db["commitMessages"].find.side_effect = mock_find 

        result = lazyCommit.generate_commit_message("empty_style")
        expected_message = "No commit messages found for style: empty_style"

        assert result == expected_message, (f"Expected '{expected_message}' but got '{result}'")

#--------------------------------------------GIT BLAME EXCUSE--------------------------------------------------

    def test_git_blame_excuse_with_data(self, mock_db):
        """
        Test case to ensure a random excuse is returned when excuses exist.
        """
        result = lazyCommit.git_blame_excuse()
        expected_excuses = ["I blame it on my partner", "I spilled my coffee"]

        assert result in expected_excuses, (
            f"Expected one of {expected_excuses} but got '{result}'"
        )

    
    def test_git_blame_excuse_empty_list(self, mock_db):
        """
        Test case to ensure the function returns 'No excuses found!' when excuses exist but the list is empty.
        """
        def mock_find():
            return [{"excuses": []}]  # Key exists but no values assigned

        mock_db["excuses"].find.side_effect = mock_find

        result = lazyCommit.git_blame_excuse()
        expected_message = "No excuses found!"

        assert result == expected_message, (
            f"Expected '{expected_message}' but got '{result}'"
        )


    def test_git_blame_excuse_no_data(self, mock_db):
        """
        Test case to ensure the function handles an empty database collection properly.
        """
        def mock_find():
            return []  # No documents in the database

        mock_db["excuses"].find.side_effect = mock_find

        result = lazyCommit.git_blame_excuse()
        expected_message = "No excuses found!"

        assert result == expected_message, (
            f"Expected '{expected_message}' but got '{result}'"
        )

#--------------------------------------------GENERATE HAIKU--------------------------------------------------

    def test_generate_haiku_with_data(self, mock_db):
        """
        Test case to ensure a random haiku is returned when haikus exist.
        """
        result = lazyCommit.generate_haiku()
        expected_haikus = ["My code flows like a river", "Like a setting sun, my code disappeared"]

        assert result in expected_haikus, (
            f"Expected one of {expected_haikus} but got '{result}'"
        )

    
    def test_generate_haiku_empty_list(self, mock_db):
        """
        Test case to ensure the function returns 'No haikus found!' when haikus exist but the list is empty.
        """
        def mock_find():
            return [{"haikus": []}]  # Key exists but no values assigned

        mock_db["haikus"].find.side_effect = mock_find

        result = lazyCommit.generate_haiku()
        expected_message = "No haikus found!"

        assert result == expected_message, (
            f"Expected '{expected_message}' but got '{result}'"
        )


    def test_generate_haiku_no_data(self, mock_db):
        """
        Test case to ensure the function handles an empty database collection properly.
        """
        def mock_find():
            return []  # No documents in the database

        mock_db["haikus"].find.side_effect = mock_find

        result = lazyCommit.generate_haiku()
        expected_message = "No haikus found!"

        assert result == expected_message, (
            f"Expected '{expected_message}' but got '{result}'"
        )
#--------------------------------------------ADD COMMIT MESSAGE --------------------------------------------------  
    
    def test_add_commit_message_empty_message(self, mock_db):
        """
        Test to ensures add_commit_message properly handles an empty message when trying to insert
        """
        result = lazyCommit.add_commit_message("professional", "")
        expected_message = "No message provided!"
        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'"  

    
    def test_add_commit_message_existing_message_existing_style(self, mock_db):  
        """
        Test to ensure that there are no duplicate messages within the same style
        """
        existing_style = "funny" 
        existing_message = "Fixed a typo that nobody noticed."
        result = lazyCommit.add_commit_message(existing_style, existing_message) 
        expected_message = f"Message already exists in the '{existing_style}' style."

        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'" 

    
    def test_add_commit_message_existing_style(self, mock_db):  
        """
        Test to ensure that a new message is added to an existing style
        """
        existing_style = "funny" 
        new_message = "Debugged a bug that wasn’t really a bug."
        result = lazyCommit.add_commit_message(existing_style, new_message) 
        expected_message = f"Message added successfully to the '{existing_style}' style."

        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'" 

    
    def test_add_commit_message_new_style(self, mock_db):  
        """
        Test to ensure that a commit message with a brand new style gets added correctly
        """
        new_style = "very serious" 
        new_message = "improve code efficiency"     
        result = lazyCommit.add_commit_message(new_style, new_message) 
        expected_message = f"Message added successfully to the '{new_style}' style."

        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'"

#--------------------------------------------ADD EXCUSE ------------------------------------------------------

    def test_add_excuse_empty_message(mock_db): 
        """
        Test case to check if an empty message is handled correctly
        """
        result = lazyCommit.add_excuse("") 
        expected_message = "No message provided!" 
        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'"   
    
    
    def test_add_excuse_existing_excuse(mock_db): 
        """
        Test case to ensure there are no duplicates
        """
        result = lazyCommit.add_excuse("I blame it on my partner") 
        expected_message = "Excuse already exists!" 
        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'" 

    
    def test_add_excuse_with_existing_excuses_list(self, mock_db):
        """
        Test case to ensure that an excuse is added correctly when an excuse array already exists 
        """
        new_excuse = "This is a new excuse."
        result = lazyCommit.add_excuse(new_excuse)
        expected_message = "Excuse added successfully."
        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'"   

    
    def test_add_excuse_successfully(self, mock_db):
        """
        Test case to ensure that an excuse is added correctly when an excuse array doesn't exists 
        """
        mock_db["excuses"].find_one.return_value = None # ensure that the collection is empty
        new_excuse = "This is a new excuse."
        result = lazyCommit.add_excuse(new_excuse)
        expected_message = "New excuse document created and excuse added successfully."
        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'"   

#--------------------------------------------ADD HAIKU --------------------------------------------------  

    def test_add_haiku_empty_message(self, mock_db):
        """
        Test case to check if an empty message is handled correctly
        """
        result = lazyCommit.add_haiku("") 
        expected_message = "No message provided!" 
        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'"   
    
    
    def test_add_haiku_existing_haiku(self, mock_db): 
        """
        Test case to ensure there are no duplicates
        """
        result = lazyCommit.add_haiku("My code flows like a river")  
        expected_message = "Haiku already exists!" 
        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'"

    
    def test_add_haiku_with_existing_haikus_list(self, mock_db):
        """
        Test case to ensure that an excuse is added correctly when an excuse array already exists 
        """
        result = lazyCommit.add_haiku("Lines of code unfold, logic dancing in the dark, bugs hide, then vanish.") 
        expected_message = "Haiku added successfully." 
        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'"  


    def test_add_haiku_added_successfully(self, mock_db): 
        """
        Test case to ensure that an excuse is added correctly when an excuse array doesn't exists 
        """
        mock_db["haikus"].find_one.return_value = None # ensure that the collection is empty
        result = lazyCommit.add_haiku("new haiku")
        expected_message = "New haiku document created and haiku added successfully."
        assert result == expected_message, f"Expected '{expected_message}' but got '{result}'"   