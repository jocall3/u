import unittest
from unittest.mock import MagicMock
from braket.comment_system import Comment, CommentSystem, AmplitudeVisibility

class TestCommentSystem(unittest.TestCase):

    def setUp(self):
        self.comment_system = CommentSystem()
        self.user1 = "user1"
        self.user2 = "user2"
        self.user3 = "user3"

    def test_add_comment(self):
        comment = self.comment_system.add_comment(self.user1, "This is a test comment.")
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.author, self.user1)
        self.assertEqual(comment.text, "This is a test comment.")
        self.assertIn(comment, self.comment_system.comments)

    def test_get_comment(self):
        comment = self.comment_system.add_comment(self.user1, "Another test comment.")
        retrieved_comment = self.comment_system.get_comment(comment.id)
        self.assertEqual(retrieved_comment, comment)

    def test_get_comment_not_found(self):
        retrieved_comment = self.comment_system.get_comment("nonexistent_id")
        self.assertIsNone(retrieved_comment)

    def test_delete_comment(self):
        comment = self.comment_system.add_comment(self.user1, "A comment to delete.")
        self.comment_system.delete_comment(comment.id)
        self.assertNotIn(comment, self.comment_system.comments)
        self.assertIsNone(self.comment_system.get_comment(comment.id))

    def test_delete_comment_not_found(self):
        with self.assertRaises(ValueError):
            self.comment_system.delete_comment("nonexistent_id")

    def test_update_comment(self):
        comment = self.comment_system.add_comment(self.user1, "Original comment.")
        self.comment_system.update_comment(comment.id, "Updated comment text.")
        updated_comment = self.comment_system.get_comment(comment.id)
        self.assertEqual(updated_comment.text, "Updated comment text.")

    def test_update_comment_not_found(self):
        with self.assertRaises(ValueError):
            self.comment_system.update_comment("nonexistent_id", "New text")

    def test_set_amplitude_visibility(self):
        comment = self.comment_system.add_comment(self.user1, "Visible comment.")
        amplitude_visibility = AmplitudeVisibility(0.8)
        self.comment_system.set_amplitude_visibility(comment.id, amplitude_visibility)
        updated_comment = self.comment_system.get_comment(comment.id)
        self.assertEqual(updated_comment.visibility, amplitude_visibility)

    def test_set_amplitude_visibility_not_found(self):
        with self.assertRaises(ValueError):
            self.comment_system.set_amplitude_visibility("nonexistent_id", AmplitudeVisibility(0.5))

    def test_is_visible_amplitude(self):
        comment = self.comment_system.add_comment(self.user1, "Amplitude-based comment.")
        amplitude_visibility = AmplitudeVisibility(0.6)
        self.comment_system.set_amplitude_visibility(comment.id, amplitude_visibility)

        # Mock the amplitude retrieval function
        self.comment_system.get_amplitude = MagicMock(return_value=0.7)
        self.assertTrue(self.comment_system.is_visible(comment.id, self.user2))

        self.comment_system.get_amplitude = MagicMock(return_value=0.5)
        self.assertFalse(self.comment_system.is_visible(comment.id, self.user2))

    def test_is_visible_no_visibility(self):
        comment = self.comment_system.add_comment(self.user1, "Always visible comment.")
        self.assertTrue(self.comment_system.is_visible(comment.id, self.user2))

    def test_is_visible_default_amplitude_function(self):
        comment = self.comment_system.add_comment(self.user1, "Amplitude-based comment.")
        amplitude_visibility = AmplitudeVisibility(0.6)
        self.comment_system.set_amplitude_visibility(comment.id, amplitude_visibility)

        # No get_amplitude function set, should raise an error
        with self.assertRaises(ValueError):
            self.comment_system.is_visible(comment.id, self.user2)

    def test_set_get_amplitude_function(self):
        def mock_get_amplitude(user_id):
            if user_id == self.user1:
                return 0.9
            elif user_id == self.user2:
                return 0.5
            else:
                return 0.0

        self.comment_system.set_amplitude_function(mock_get_amplitude)
        comment = self.comment_system.add_comment(self.user1, "Amplitude-based comment.")
        amplitude_visibility = AmplitudeVisibility(0.6)
        self.comment_system.set_amplitude_visibility(comment.id, amplitude_visibility)

        self.assertTrue(self.comment_system.is_visible(comment.id, self.user1))
        self.assertFalse(self.comment_system.is_visible(comment.id, self.user2))

    def test_clear_comments(self):
        self.comment_system.add_comment(self.user1, "Comment 1")
        self.comment_system.add_comment(self.user2, "Comment 2")
        self.comment_system.clear_comments()
        self.assertEqual(len(self.comment_system.comments), 0)

if __name__ == '__main__':
    unittest.main()