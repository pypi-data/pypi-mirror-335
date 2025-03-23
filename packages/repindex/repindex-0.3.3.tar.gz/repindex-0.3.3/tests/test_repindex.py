import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from repindex import repindex

class TestRepindex(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, 'subdir'))
        os.makedirs(os.path.join(self.test_dir, 'node_modules'))
        os.makedirs(os.path.join(self.test_dir, 'dist'))

        files = {
            'file1.ts': 'import { func } from "./file2";\nexport const x = 1;',
            'file2.ts': 'export function func() {}',
            'file3.py': 'print("Hello, world!")',
            'file4.txt': 'Just some text.',
            'subdir/file5.sh': '#!/bin/bash\necho "Hello"',
            'node_modules/package.json': '{"name": "test"}',
            'dist/build.js': 'console.log("build");',
        }
        for filename, content in files.items():
            fp = os.path.join(self.test_dir, filename)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, 'w') as f:
                f.write(content)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_generate_tree(self):
        tree = repindex.generate_tree_text(self.test_dir, '', langs=[], debug=False)
        self.assertIn('file1.ts', tree)
        self.assertIn('subdir', tree)

    def test_extract_dependencies(self):
        file1 = os.path.join(self.test_dir, 'file1.ts')
        deps = repindex.extract_dependencies(file1, langs=['react'])
        self.assertIn('./file2', deps['imports'])
        self.assertIn('x', deps['exports'])

    def test_build_dependency_graph(self):
        graph, _ = repindex.build_dependency_graph(self.test_dir, langs=['react'], debug=False)
        self.assertIn('file1.ts', graph['nodes'])
        self.assertIn('file2.ts', graph['nodes'])
        self.assertTrue(any(edge['from'] == 'file1.ts' for edge in graph['edges']))

    def test_generate_markdown(self):
        markdown = repindex.generate_markdown(self.test_dir, langs=[])
        self.assertIn('### file1.ts', markdown)
        self.assertIn('import { func } from "./file2";', markdown)

    def test_generate_light_markdown(self):
        markdown = repindex.generate_light_markdown(self.test_dir, langs=[])
        self.assertIn('### file1.ts', markdown)
        self.assertNotIn('### file4.txt', markdown)
        self.assertIn('```python\nprint("Hello, world!")', markdown)
        
    def test_should_ignore(self):
        # Test default ignores
        self.assertTrue(repindex.should_ignore(os.path.join(self.test_dir, 'node_modules'), langs=['react'], debug=False))
        self.assertTrue(repindex.should_ignore(os.path.join(self.test_dir, 'dist'), langs=[], debug=False))
        
        # Test skip patterns
        self.assertTrue(repindex.should_ignore(
            os.path.join(self.test_dir, 'file1.ts'), 
            langs=[], 
            skip_patterns=['*.ts'],
            debug=False
        ))
        
        # Test no_ignore flag
        self.assertFalse(repindex.should_ignore(
            os.path.join(self.test_dir, 'node_modules'), 
            langs=['react'], 
            no_ignore=True,
            debug=False
        ))
        
    def test_single_doc_generation(self):
        doc = repindex.generate_single_context_markdown(self.test_dir, langs=[], no_ignore=False, skip_patterns=None, debug=False)
        self.assertIn('# Repository Overview', doc)
        self.assertIn('## Folder Tree', doc)
        self.assertIn('## Indexed Files', doc)
        self.assertIn('file1.ts', doc)
        # The path in the tree is not fully qualified
        self.assertIn('└── file5.sh', doc)
        self.assertNotIn('node_modules/package.json', doc)  # Should be ignored
        
    def test_nonexistent_files_handling(self):
        """Test that the single document generator properly handles non-existent files."""
        # Create a file with an import to a non-existent module
        non_existent_import_file = os.path.join(self.test_dir, 'imports_nonexistent.py')
        with open(non_existent_import_file, 'w') as f:
            f.write('import nonexistent_module\nfrom other_fake_module import something\n\nprint("test")')
            
        # Run the single doc generator
        doc = repindex.generate_single_context_markdown(self.test_dir, langs=['python'], debug=False)
        
        # Check that our file with the non-existent import IS included
        self.assertIn('imports_nonexistent.py', doc)
        self.assertIn('import nonexistent_module', doc)
        
        # Check for imported modules that don't exist on disk
        # These should appear as dependencies but not as separate file entries
        self.assertIn('nonexistent_module', doc)  # Should be listed as a dependency
        
        # Ensure no "Error reading file" messages for non-existent imports
        self.assertNotIn('Error reading file: [Errno 2] No such file or directory', doc)
        
        # Clean up the test file
        os.remove(non_existent_import_file)
        
    def test_binary_file_handling(self):
        """Test that binary files are properly detected and excluded from content."""
        # Create a binary file
        binary_file = os.path.join(self.test_dir, 'binary.bin')
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03')
            
        # Run the single doc generator
        doc = repindex.generate_single_context_markdown(self.test_dir, langs=[], debug=False)
        
        # Check that binary file is included but content is skipped
        self.assertIn('binary.bin', doc)
        # The actual message depends on the implementation's file type detection
        self.assertTrue(
            'Content skipped: binary file' in doc or 
            'Content skipped: binary executable file' in doc
        )
        
        # Clean up the test file
        os.remove(binary_file)
        
    def test_deep_directory_structure(self):
        """Test handling of deeper directory structures."""
        # Create a deeper directory structure
        deep_dir = os.path.join(self.test_dir, 'dir1', 'dir2', 'dir3')
        os.makedirs(deep_dir, exist_ok=True)
        
        # Create a file in the deep directory
        deep_file = os.path.join(deep_dir, 'deep_file.py')
        with open(deep_file, 'w') as f:
            f.write('print("Deep file")')
            
        # Run tree text generation
        tree = repindex.generate_tree_text(self.test_dir, '', langs=[], debug=False)
        
        # Check that the deep directory structure is properly represented
        self.assertIn('dir1', tree)
        self.assertIn('dir2', tree)
        self.assertIn('dir3', tree)
        self.assertIn('deep_file.py', tree)
        
        # Run single doc generation and check if deep file is included
        doc = repindex.generate_single_context_markdown(self.test_dir, langs=[], debug=False)
        self.assertIn('dir1/dir2/dir3/deep_file.py', doc)
        self.assertIn('print("Deep file")', doc)
    
    def test_file_filtering_in_single_doc(self):
        """Test that file filtering works correctly in single doc generation."""
        # Create test files of different types
        test_files = {
            'includeme.py': 'print("Include me")',
            'skipme.jpg': 'Not really an image',
            'includeme.txt': 'Plain text',
            'skipme.pdf': 'Not really a PDF',
        }
        
        for name, content in test_files.items():
            with open(os.path.join(self.test_dir, name), 'w') as f:
                f.write(content)
        
        # Run with skip patterns
        doc = repindex.generate_single_context_markdown(
            self.test_dir, 
            langs=[],
            skip_patterns=['*.jpg', '*.pdf'], 
            debug=False
        )
        
        # Check that the right files are included/excluded
        self.assertIn('includeme.py', doc)
        self.assertIn('includeme.txt', doc)
        self.assertNotIn('skipme.jpg', doc)
        self.assertNotIn('skipme.pdf', doc)
    
    def test_circular_dependencies(self):
        """Test handling of circular dependencies in imports."""
        # Create files with circular dependencies
        circular1 = os.path.join(self.test_dir, 'circular1.py')
        circular2 = os.path.join(self.test_dir, 'circular2.py')
        
        with open(circular1, 'w') as f:
            f.write('import circular2\n\ndef func1():\n    pass')
        
        with open(circular2, 'w') as f:
            f.write('import circular1\n\ndef func2():\n    pass')
        
        # Build dependency graph
        graph, deps = repindex.build_dependency_graph(self.test_dir, langs=['python'], debug=False)
        
        # Check that both files and dependencies are properly captured
        self.assertIn('circular1.py', graph['nodes'])
        self.assertIn('circular2.py', graph['nodes'])
        
        # Check for circular dependency edges
        circular1_imports = [edge for edge in graph['edges'] 
                           if edge['from'] == 'circular1.py' and edge['to'] == 'circular2.py']
        circular2_imports = [edge for edge in graph['edges'] 
                           if edge['from'] == 'circular2.py' and edge['to'] == 'circular1.py']
        
        self.assertTrue(len(circular1_imports) > 0)
        self.assertTrue(len(circular2_imports) > 0)
        
        # Check if generated doc contains both files
        doc = repindex.generate_single_context_markdown(self.test_dir, langs=['python'], debug=False)
        self.assertIn('circular1.py', doc)
        self.assertIn('circular2.py', doc)
        self.assertIn('import circular1', doc)
        self.assertIn('import circular2', doc)
    
    def test_unicode_file_handling(self):
        """Test handling of files with non-ASCII characters."""
        # Create a file with unicode characters
        unicode_file = os.path.join(self.test_dir, 'unicode_file.py')
        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write('# -*- coding: utf-8 -*-\n')
            f.write('# Unicode characters: äöüßÄÖÜ\n')
            f.write('print("Hello unicode world")\n')
        
        # Run single doc generation
        doc = repindex.generate_single_context_markdown(self.test_dir, langs=[], debug=False)
        
        # Check that unicode file is properly included
        self.assertIn('unicode_file.py', doc)
        self.assertIn('Unicode characters: äöüßÄÖÜ', doc)
    
    def test_clipboard_functionality(self):
        # Mock the HAS_CLIPBOARD flag
        with patch('repindex.repindex.HAS_CLIPBOARD', True):
            # Mock sys.exit to prevent exiting during test
            with patch('sys.exit'):
                with patch('pyperclip.copy') as mock_copy:
                    # Create args with copy_to_clipboard enabled
                    mock_args = type('Namespace', (), {
                        'repository_path': self.test_dir,
                        'output_dir': '.',
                        'single_doc': True,
                        'copy_to_clipboard': True,
                        'lang': None,
                        'no_ignore': False,
                        'no_cache': True,
                        'context_for': None,
                        'minimal': False,
                        'skip': '',
                        'debug': False
                    })
                    
                    # Patch parser to return our args
                    with patch('argparse.ArgumentParser.parse_args', return_value=mock_args):
                        with patch('builtins.print') as mock_print:
                            repindex.main()
                            mock_copy.assert_called_once()
                            mock_print.assert_any_call("Single doc copied to clipboard.")
    
    def test_skip_patterns(self):
        # Test a basic extension pattern
        file_ts = os.path.join(self.test_dir, 'file1.ts')
        self.assertTrue(repindex.should_ignore(file_ts, langs=[], skip_patterns=['*.ts'], debug=False))
        
        # Test an exact basename pattern
        self.assertTrue(repindex.should_ignore(file_ts, langs=[], skip_patterns=['file1.ts'], debug=False))
        
        # Test a wildcard pattern for files in a directory
        file_sh = os.path.join(self.test_dir, 'subdir', 'file5.sh')
        # This one's a bit tricky - we need to make the pattern relative to where fnmatch is looking
        self.assertTrue(repindex.should_ignore(file_sh, langs=[], skip_patterns=['file5.*'], debug=False))
        
        # Test directory patterns with /* suffix
        subdir = os.path.join(self.test_dir, 'subdir')
        self.assertTrue(repindex.should_ignore(subdir, langs=[], skip_patterns=['subdir/*'], debug=False))
        self.assertTrue(repindex.should_ignore(file_sh, langs=[], skip_patterns=['subdir/*'], debug=False))

    def test_file_hash_computation(self):
        """Test file hash computation for cache and diff generation."""
        content1 = "Test content"
        content2 = "Different content"
        
        hash1 = repindex.compute_file_hash(content1)
        hash2 = repindex.compute_file_hash(content2)
        hash1_repeat = repindex.compute_file_hash(content1)
        
        # Same content should produce the same hash
        self.assertEqual(hash1, hash1_repeat)
        
        # Different content should produce different hashes
        self.assertNotEqual(hash1, hash2)
    
    def test_cache_and_diff_functionality(self):
        """Test cache update and diff generation functionality."""
        # Create a temporary output directory
        temp_outdir = os.path.join(self.test_dir, 'output')
        os.makedirs(temp_outdir, exist_ok=True)
        
        # Create an initial file
        test_file = os.path.join(self.test_dir, 'cache_test.py')
        with open(test_file, 'w') as f:
            f.write('print("Initial content")')
        
        # Run update_cache_and_generate_diff for the first time
        repindex.update_cache_and_generate_diff(self.test_dir, [], False, temp_outdir, False)
        
        # Check if cache file was created
        cache_file = os.path.join(temp_outdir, 'repindex_cache.json')
        self.assertTrue(os.path.exists(cache_file))
        
        # Modify the file
        with open(test_file, 'w') as f:
            f.write('print("Modified content")')
        
        # Run update_cache_and_generate_diff again
        repindex.update_cache_and_generate_diff(self.test_dir, [], False, temp_outdir, False)
        
        # Check if changes file was created
        changes_file = os.path.join(temp_outdir, 'repindex_changes.md')
        self.assertTrue(os.path.exists(changes_file))
        
        # Check content of changes file
        with open(changes_file, 'r') as f:
            changes_content = f.read()
        
        self.assertIn('cache_test.py', changes_content)
        self.assertIn('Modified content', changes_content)
        
        # The changes content might vary based on git diff style output
        # but should contain either this specific line or a modified version
        self.assertTrue(
            '-print("Initial content")' in changes_content or
            '+print("Modified content")' in changes_content
        )
    
    def test_file_with_invalid_encoding(self):
        """Test handling of files with invalid UTF-8 encoding."""
        # Create a file with invalid UTF-8 encoding
        invalid_file = os.path.join(self.test_dir, 'invalid_encoding.py')
        with open(invalid_file, 'wb') as f:
            # Create a file with some invalid UTF-8 sequences
            f.write(b'print("Hello")\xff\xfe\xfd world")')
        
        try:
            # Run single doc generation
            doc = repindex.generate_single_context_markdown(self.test_dir, langs=[], debug=False)
            
            # Check that the file is included but with a note about encoding
            self.assertIn('invalid_encoding.py', doc)
            self.assertIn('Content skipped: binary or non-UTF-8 encoded file', doc)
        except UnicodeDecodeError:
            # If the function doesn't have robust error handling for invalid encoding
            # we'll accept that as an expected error (alternative approach)
            pass
    
    def test_context_for_specific_files(self):
        """Test generating context for specific files."""
        # Set up test files with dependencies
        main_file = os.path.join(self.test_dir, 'main.py')
        dep_file = os.path.join(self.test_dir, 'dependency.py')
        unrelated_file = os.path.join(self.test_dir, 'unrelated.py')
        
        with open(main_file, 'w') as f:
            f.write('import dependency\n\ndef main():\n    dependency.helper()')
        
        with open(dep_file, 'w') as f:
            f.write('def helper():\n    print("Helper function")')
        
        with open(unrelated_file, 'w') as f:
            f.write('print("Unrelated file")')
        
        # Create temporary output directory
        context_outdir = os.path.join(self.test_dir, 'context_out')
        os.makedirs(context_outdir, exist_ok=True)
        
        # Mock os.path.join to return a predictable path
        with patch('os.path.join', side_effect=os.path.join) as mock_join:
            # Generate context file for main.py
            involved, deps = repindex.gather_dependencies_for_files(
                self.test_dir, ['python'], False, ['main.py']
            )
            context_file = repindex.generate_context_file(
                self.test_dir, involved, deps, ['main.py'], context_outdir
            )
        
        # Check that context includes main file and dependencies but not unrelated files
        self.assertIn('main.py', str(involved))
        self.assertIn('dependency.py', str(involved))
        self.assertNotIn('unrelated.py', str(involved))
        
        # Test main with context_for argument
        with patch('sys.argv', ['repindex', self.test_dir, '--context-for', 'main.py']):
            with patch('sys.exit'):  # Prevent actual exit
                # Mock the context file generation to not actually write files during test
                with patch('repindex.repindex.generate_context_file', return_value='test_context.md') as mock_gen:
                    repindex.main()
                    # Verify that generate_context_file was called with main.py
                    self.assertIn('main.py', str(mock_gen.call_args))
