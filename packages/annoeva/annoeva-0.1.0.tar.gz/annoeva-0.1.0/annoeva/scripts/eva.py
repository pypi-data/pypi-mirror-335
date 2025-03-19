#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto bioinformatics workflow monitor system for SGE environment.

This module provides a command-line interface for monitoring and managing
bioinformatics workflows in an SGE cluster environment.

Features:
- Project monitoring and status tracking
- Automatic pipeline execution
- Cron-based job management
- Project statistics and reporting
"""

import os
import warnings
from typing import Optional

import click

from annoeva.db import cron, addproject, rerun, stat, dele
from annoeva.config import cronlist, personal_config

# Suppress warnings
warnings.filterwarnings("ignore")

@click.group()
def main() -> None:
    """Main command group for annoeva CLI.
    
    This serves as the entry point for all subcommands.
    """
    pass

# ------------------------------------------------------------------------------------
@main.command(name="addproject")
@click.option('--projectid', '-p', default=None,
              help="Unique project identifier (e.g., 'XS05KF23080-21')")
@click.option('--pipetype', '-t', default='scrna',
              help="Pipeline type (default: 'scrna')")
@click.option('--workdir', '-d', required=True,
              help="Project working directory containing info/, Filter/, and Analysis/ subdirectories")
def addproject_cli(projectid: Optional[str], pipetype: str, workdir: str) -> None:
    """Add a new project to the monitoring system.
    
    Args:
        projectid: Unique identifier for the project
        pipetype: Type of analysis pipeline to use
        workdir: Path to project directory containing required subdirectories
        
    The system will automatically start analysis if both info/info.xlsx and 
    Filter/go.sign files are detected in the project directory.
    """
    addproject(projectid, pipetype, workdir)

# ------------------------------------------------------------------------------------
@main.command(name="stat")
@click.option('--projectid', '-p', default=None,
              help="Project ID to show detailed statistics. If not provided, shows summary for all projects")
def stat_cli(projectid: Optional[str]) -> None:
    """Display project statistics and status.
    
    Args:
        projectid: Optional project identifier. When provided, shows detailed
                   stdout/stderr for the specific project. When omitted, shows
                   summary statistics for all monitored projects.
    """
    stat(projectid)

# ------------------------------------------------------------------------------------
@main.command(name="rerun")
@click.option('--projectid', '-p', required=True,
              help="Project ID to resubmit")
def rerun_cli(projectid: str) -> None:
    """Resubmit a project's analysis jobs.
    
    Args:
        projectid: Identifier of the project to resubmit
        
    This command will re-run the project's analysis pipeline by executing
    the work_qsubsge.sh script.
    """
    rerun(projectid)

# ------------------------------------------------------------------------------------
@main.command(name="delete")
@click.option('--projectid', '-p', required=True,
              help="Space-separated list of project IDs to delete")
def delete_cli(projectid: str) -> None:
    """Remove projects from the monitoring system.
    
    Args:
        projectid: Space-separated list of project identifiers to remove
        
    This command permanently removes the specified projects from the
    annoeva database and stops any ongoing monitoring.
    """
    dele(projectid)

# ------------------------------------------------------------------------------------
@main.command(name="cron")
@click.option('--mode', '-m', default=1, type=click.IntRange(1, 2),
              help="Cron job mode: 1 - Update database, 2 - Cleanup old projects")
def cron_cli(mode: int) -> None:
    """Perform scheduled maintenance tasks.
    
    Args:
        mode: Operation mode (1 or 2)
            1: Check and update the AutoFlow database
            2: Clean up projects finished or failed more than a month ago
    """
    cron(mode)

# ------------------------------------------------------------------------------------
if __name__ == '__main__':
    personal_config()
    crnlist = cronlist(confpath='~/.annoeva/commander.yml', commanderpath=os.path.abspath(__file__))
    crnlist.add_cron()
    main()
