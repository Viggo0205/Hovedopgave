"""
Direct test launcher for the MCP server tools.

This script allows you to test MCP tools directly without the MCP framework.
Run: python test_direct.py
"""

import asyncio
import os
import sys

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_tools_directly():
    """Direct testing mode - test MCP tools without MCP framework."""
    print("🧪 DIRECT TOOL TESTING MODE")
    print("=" * 50)
    
    # Import components to build the tools manually
    from developer_skill_analyzer.config import Config
    from developer_skill_analyzer.analyzers.github_analyzer import GitHubAnalyzer
    from developer_skill_analyzer.analyzers.jira_analyzer import JiraAnalyzer
    from developer_skill_analyzer.analyzers.skill_processor import SkillProcessor
    from datetime import datetime
    
    # Load configuration
    config = Config()
    
    if not config.github_token:
        print("⚠️ Warning: No GitHub token configured")
        print("Set GITHUB_TOKEN environment variable for full functionality")
        return
    
    while True:
        print("\nAvailable tools:")
        print("1. get_all_employees - Discover collaborators")
        print("2. analyze_github_developer - Analyze a developer") 
        print("3. get_technical_stack - Organization tech stack")
        print("4. get_skill_summary - Combined skill assessment")
        print("5. compare_developers - Compare two developers")
        print("\nQuick tests:")
        print("8. Quick validation (imports & config)")
        print("9. Test employee formats")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-5): ").strip()
        
        if choice == "0":
            print("Exiting direct test mode...")
            break
        
        elif choice == "1":
            print("\n--- Testing get_all_employees ---")
            source = input("Source (github/jira/all) [github]: ").strip() or "github"
            metadata = input("Include metadata? (y/n) [n]: ").strip().lower() == 'y'
            active = input("Filter active only? (y/n) [y]: ").strip().lower() != 'n'
            
            print("🔍 Running collaborator discovery...")
            try:
                employees = {
                    "github_employees": [],
                    "jira_employees": [],
                    "total_count": 0,
                    "source": source,
                    "metadata": {}
                }
                
                # Discover collaborators from GitHub repositories
                if source in ["github", "all"] and config.github_token:
                    print("Discovering GitHub collaborators...")
                    print("⚡ Using quick mode (analyzing max 10 repositories)")
                    analyzer = GitHubAnalyzer(config.github_token)
                    github_employees = await analyzer.discover_collaborators(
                        include_metadata=metadata,
                        filter_active=active,
                        max_repositories=10  # Limit for faster testing
                    )
                    employees["github_employees"] = github_employees
                    print(f"✅ Found {len(github_employees)} GitHub collaborators")
                    
                    if github_employees:
                        print("📋 Sample GitHub collaborators:")
                        for i, emp in enumerate(github_employees[:3]):
                            if isinstance(emp, dict):
                                print(f"   {i+1}. {emp.get('username', emp)}")
                            else:
                                print(f"   {i+1}. {emp}")
                
                # Calculate totals
                total_github = len(employees["github_employees"])
                employees["total_count"] = total_github
                
                employees["metadata"] = {
                    "github_total": total_github,
                    "query_timestamp": datetime.now().isoformat(),
                    "include_metadata": metadata,
                    "filter_active": active
                }
                
                print(f"✅ Total collaborators found: {employees['total_count']}")
                        
            except Exception as e:
                print(f"❌ Test failed: {e}")
                import traceback
                traceback.print_exc()
        
        elif choice == "2":
            print("\n--- Testing analyze_github_developer ---")
            username = input("GitHub username [Viggo0205]: ").strip() or "Viggo0205"
            months = input("Time range months [6]: ").strip() or "6"
            
            try:
                months = int(months)
                print(f"🔍 Analyzing developer: {username}")
                
                analyzer = GitHubAnalyzer(config.github_token)
                
                # Perform the analysis
                analysis_result = await analyzer.analyze_developer(
                    username=username,
                    repositories=None,
                    include_contributions=True,
                    time_range_months=months
                )
                
                # Process skills using the skill processor
                skill_processor = SkillProcessor()
                skill_assessment = skill_processor.process_github_data(analysis_result)
                
                result = {
                    "developer": username,
                    "analysis_type": "github",
                    "data_source": "real_api",
                    "time_range_months": months,
                    "skill_assessment": skill_assessment,
                    "analysis_date": analysis_result.get("analysis_date"),
                    "summary": skill_assessment.get("summary", {}),
                    "detailed_skills": skill_assessment.get("skills", {}),
                    "recommendations": skill_assessment.get("recommendations", [])
                }
                
                print(f"✅ Analysis complete for {result['developer']}")
                print(f"   Analysis type: {result.get('analysis_type', 'unknown')}")
                print(f"   Data source: {result.get('data_source', 'unknown')}")
                
                skills = result.get('detailed_skills', {})
                if skills:
                    print(f"   Skills found: {list(skills.keys())}")
                        
            except ValueError:
                print("Invalid number of months")
            except Exception as e:
                print(f"❌ Test failed: {e}")
                import traceback
                traceback.print_exc()
        
        elif choice == "3":
            print("\n--- Testing get_technical_stack ---")
            print("🔍 Analyzing organization tech stack...")
            
            try:
                analyzer = GitHubAnalyzer(config.github_token)
                stack_data = await analyzer.get_organization_tech_stack()
                
                result = {
                    "data_source": "real_api",
                    "stack": stack_data.get("technologies", {}),
                    "summary": stack_data.get("summary", {}),
                    "analysis_date": datetime.now().isoformat(),
                    "total_repositories_analyzed": stack_data.get("repositories_count", 0)
                }
                
                print(f"✅ Tech stack analysis complete")
                print(f"   Repositories analyzed: {result.get('total_repositories_analyzed', 0)}")
                
                technologies = result.get('stack', {})
                if technologies:
                    print(f"   Technology categories: {list(technologies.keys())}")
                    
                    # Show programming languages if available
                    languages = technologies.get('programming_languages', {})
                    if languages:
                        print(f"   Top languages: {list(languages.keys())[:5]}")
                            
            except Exception as e:
                print(f"❌ Test failed: {e}")
                import traceback
                traceback.print_exc()
        
        elif choice == "4":
            print("\n--- Testing get_skill_summary ---")
            github_user = input("GitHub username (optional) [Viggo0205]: ").strip() or "Viggo0205"
            jira_email = input("Jira email (optional): ").strip() or None
            
            if github_user or jira_email:
                print(f"🔍 Generating skill summary...")
                try:
                    analyzer = GitHubAnalyzer(config.github_token)
                    jira_analyzer = JiraAnalyzer(
                        server_url=config.jira_server_url,
                        email=config.jira_email,
                        api_token=config.jira_api_token
                    ) if config.jira_email and config.jira_api_token else None
                    skill_processor = SkillProcessor()
                    
                    # Get GitHub data if username provided
                    github_data = {}
                    if github_user:
                        github_data = await analyzer.analyze_developer(github_user)
                    
                    # Get Jira data if available
                    jira_data = {}
                    if jira_analyzer and jira_email:
                        try:
                            jira_data = await jira_analyzer.analyze_developer(jira_email)
                        except Exception as e:
                            print(f"Warning: Jira analysis failed: {e}")
                    
                    # Process skills
                    skills = []
                    if github_data:
                        skills = skill_processor.process_github_data(github_data)
                    if jira_data:
                        skills = skill_processor.merge_jira_skills(skills, jira_data)
                    
                    # Create summary
                    top_skills = [skill.name for skill in skills[:10]]  # Top 10 skills
                    
                    result = {
                        "developer_identifiers": {
                            "github_username": github_user if github_user else None,
                            "jira_email": jira_email if jira_email else None
                        },
                        "top_skills": top_skills,
                        "total_skills": len(skills),
                        "analysis_date": datetime.now().isoformat(),
                        "data_sources": {
                            "github": bool(github_data),
                            "jira": bool(jira_data)
                        }
                    }
                    
                    print(f"✅ Skill summary complete")
                    identifiers = result.get('developer_identifiers', {})
                    print(f"   GitHub: {identifiers.get('github_username', 'None')}")
                    print(f"   Jira: {identifiers.get('jira_email', 'None')}")
                    print(f"   Total skills: {result.get('total_skills', 0)}")
                    
                    top_skills = result.get('top_skills', [])
                    if top_skills:
                        print(f"   Top skills: {top_skills[:3]}")
                            
                except Exception as e:
                    print(f"❌ Test failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("At least one identifier required")
        
        elif choice == "5":
            print("\n--- Testing compare_developers ---")
            dev1 = input("First developer GitHub username [Viggo0205]: ").strip() or "Viggo0205"
            dev2 = input("Second developer GitHub username: ").strip()
            
            if dev1 and dev2:
                print(f"🔍 Comparing {dev1} vs {dev2}...")
                try:
                    analyzer = GitHubAnalyzer(config.github_token)
                    skill_processor = SkillProcessor()
                    
                    # Analyze both developers
                    print(f"  📊 Analyzing {dev1}...")
                    dev1_data = await analyzer.analyze_developer(dev1)
                    dev1_skills = skill_processor.process_github_data(dev1_data)
                    
                    print(f"  📊 Analyzing {dev2}...")
                    dev2_data = await analyzer.analyze_developer(dev2)
                    dev2_skills = skill_processor.process_github_data(dev2_data)
                    
                    # Create comparison
                    dev1_skill_names = [skill.name for skill in dev1_skills]
                    dev2_skill_names = [skill.name for skill in dev2_skills]
                    
                    common_skills = set(dev1_skill_names) & set(dev2_skill_names)
                    dev1_unique = set(dev1_skill_names) - set(dev2_skill_names)
                    dev2_unique = set(dev2_skill_names) - set(dev1_skill_names)
                    
                    result = {
                        "developers": {
                            "developer1": dev1,
                            "developer2": dev2
                        },
                        "comparison_type": "skills_comparison",
                        "comparison_date": datetime.now().isoformat(),
                        "comparison": {
                            "common_skills": list(common_skills),
                            "developer1_unique_skills": list(dev1_unique),
                            "developer2_unique_skills": list(dev2_unique),
                            "skill_counts": {
                                "developer1": len(dev1_skills),
                                "developer2": len(dev2_skills),
                                "common": len(common_skills)
                            }
                        },
                        "summary": {
                            "similarity_score": len(common_skills) / max(len(dev1_skills), len(dev2_skills)) if max(len(dev1_skills), len(dev2_skills)) > 0 else 0,
                            "total_unique_skills": len(common_skills | dev1_unique | dev2_unique)
                        }
                    }
                    
                    print(f"✅ Comparison complete")
                    devs = result.get('developers', {})
                    print(f"   Developer 1: {devs.get('developer1', 'Unknown')} ({result['comparison']['skill_counts']['developer1']} skills)")
                    print(f"   Developer 2: {devs.get('developer2', 'Unknown')} ({result['comparison']['skill_counts']['developer2']} skills)")
                    print(f"   Common skills: {result['comparison']['skill_counts']['common']}")
                    print(f"   Similarity: {result['summary']['similarity_score']:.1%}")
                        
                except Exception as e:
                    print(f"❌ Test failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Both usernames required")
                
        elif choice == "8":
            print("\n--- Quick Validation ---")
            print("🧪 Testing imports and configuration...")
            
            try:
                print("✅ All imports successful")
                print(f"✅ Configuration loaded")
                print(f"   GitHub token: {'✓ Present' if config.github_token else '✗ Missing'}")
                print(f"   Jira config: {'✓ Present' if config.jira_email and config.jira_api_token else '✗ Missing'}")
                
                if config.github_token:
                    analyzer = GitHubAnalyzer(config.github_token)
                    print("✅ GitHubAnalyzer instantiated")
                    
                    # Test that the methods exist
                    assert hasattr(analyzer, 'discover_collaborators'), "discover_collaborators method missing"
                    assert hasattr(analyzer, 'get_organization_tech_stack'), "get_organization_tech_stack method missing"
                    assert hasattr(analyzer, 'analyze_developer'), "analyze_developer method missing"
                    print("✅ All required methods exist")
                
                skill_processor = SkillProcessor()
                print("✅ SkillProcessor instantiated")
                print("\n🎉 Quick validation completed successfully!")
                print("✅ Direct testing mode is ready to use")
                
            except Exception as e:
                print(f"❌ Quick validation failed: {e}")
                import traceback
                traceback.print_exc()
                
        elif choice == "9":
            print("\n--- Testing Employee Formats ---")
            print("🧪 Testing get_all_employees output formats...")
            
            try:
                from developer_skill_analyzer.server import get_all_employees
                
                print("\n📋 Testing WITHOUT metadata:")
                print("-" * 30)
                result1 = await get_all_employees(
                    source="github",
                    include_metadata=False,
                    filter_active=True
                )
                print(f"Result structure: {type(result1)}")
                if isinstance(result1, dict):
                    github_employees = result1.get('github_employees', [])
                    print(f"GitHub employees count: {len(github_employees)}")
                    if github_employees:
                        print(f"First employee: {github_employees[0]}")
                        print(f"Employee type: {type(github_employees[0])}")
                
                print("\n📊 Testing WITH metadata:")
                print("-" * 30)
                result2 = await get_all_employees(
                    source="github", 
                    include_metadata=True,
                    filter_active=False
                )
                if isinstance(result2, dict):
                    github_employees = result2.get('github_employees', [])
                    print(f"GitHub employees count: {len(github_employees)}")
                    if github_employees:
                        emp = github_employees[0]
                        print(f"First employee type: {type(emp)}")
                        if isinstance(emp, dict):
                            print(f"Employee data keys: {list(emp.keys())}")
                            print(f"Username: {emp.get('username', 'Unknown')}")
                            print(f"Repositories: {emp.get('total_repositories', 0)}")
                            
                print("\n✅ Employee format testing completed!")
                        
            except Exception as e:
                print(f"❌ Employee format test failed: {e}")
                import traceback
                traceback.print_exc()
        
        else:
            print("Invalid choice")


if __name__ == "__main__":
    print("🚀 MCP Server Direct Testing Tool")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        asyncio.run(test_tools_directly())
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()