# -*- coding: utf-8 -*-
"""Python_Implementation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Zdzr0ASQt-20lPDcISIcTNyfv_BwSXLB
"""

import openpyxl
import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment
from heapq import heappush, heappop

# Worker Class
class Worker:
    def __init__(self, id):
        self.id = id  # Unique identifier for the worker
        self.tasks = []  # List to hold assigned tasks
        self.total_score = 0  # Total skill score for the worker

    def assign_task(self, task_index, score):
        """Assign a task to the worker and update the total score."""
        self.tasks.append(task_index)
        self.total_score += score

    def can_take_more_tasks(self, max_tasks):
        """Check if the worker can take on more tasks."""
        return len(self.tasks) < max_tasks

    def __str__(self):
        """String representation of the worker for easy debugging."""
        return f"Worker {self.id}: Tasks {self.tasks}, Total Score: {self.total_score}"

# Load skill scores from Excel file
def load_skill_scores_from_excel(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    task_names = [cell.value for cell in sheet[1]][1:]  # Skip the first column (Worker IDs)
    workers_data = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        worker_id = row[0]
        skill_scores = list(row[1:])
        workers_data.append([worker_id] + skill_scores)
    df = pd.DataFrame(workers_data, columns=['Worker ID'] + task_names)
    return df

# Task Assignment with Constraints for fewer workers than tasks
def maximize_skill_score_with_constraints(skill_matrix, num_tasks, absent_count):
    num_workers = skill_matrix.shape[0]
    max_multiple_tasks_workers = absent_count -2 # Strictly less than the number of absent employees
    workers_with_multiple_tasks = 0

    task_heap = []
    for i in range(num_workers):
        for j in range(num_tasks):
            if skill_matrix[i, j] > 0:
                heappush(task_heap, (-skill_matrix[i, j], i, j))

    assignments = []
    total_skill_score = 0
    workers = [Worker(i) for i in range(num_workers)]
    assigned_tasks = set()

    while len(assigned_tasks) < num_tasks:
        if task_heap:
            neg_score, worker_id, task_id = heappop(task_heap)
            score = -neg_score

            if task_id in assigned_tasks or score == 0:
                continue

            max_tasks = 2 if (len(workers[worker_id].tasks) == 0 and workers_with_multiple_tasks < max_multiple_tasks_workers) else 1
            if workers[worker_id].can_take_more_tasks(max_tasks):

                workers[worker_id].assign_task(task_id, score)
                assigned_tasks.add(task_id)
                total_skill_score += score
                assignments.append((worker_id, task_id))


                if len(workers[worker_id].tasks) == 2:
                    workers_with_multiple_tasks += 1
        else:

            for worker_id in range(num_workers):
                for task_id in range(num_tasks):
                    if task_id not in assigned_tasks and skill_matrix[worker_id, task_id] > 0:
                        workers[worker_id].assign_task(task_id, skill_matrix[worker_id, task_id])
                        assigned_tasks.add(task_id)
                        total_skill_score += skill_matrix[worker_id, task_id]
                        assignments.append((worker_id, task_id))
                        break

    return assignments, total_skill_score

# More Workers or Equal Case
def hungarian_task_assignment(skill_matrix, num_tasks):

    num_workers = skill_matrix.shape[0]
    cost_matrix = skill_matrix * -1
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    assignments = [(row, col) for row, col in zip(row_ind, col_ind)]
    total_skill_score = skill_matrix[row_ind, col_ind].sum()

    return assignments, total_skill_score

# Main function to read data, apply the algorithm, and print results
def workers_assignment_problem_with_constraints(file_path):

    absent_employees_input = input("Are there any absent employees? (yes/no): ").strip().lower()
    absent_employees = []
    if absent_employees_input == "yes":
        absent_employees = input("Enter the absent employee IDs (comma-separated): ").strip().split(",")
        absent_employees = [emp.strip() for emp in absent_employees]
    df = load_skill_scores_from_excel(file_path)


    if absent_employees:
        df = df[~df['Worker ID'].isin(absent_employees)]

    skill_matrix = df.drop(columns=['Worker ID']).values
    num_tasks = skill_matrix.shape[1]
    num_workers = skill_matrix.shape[0]

    if num_workers >= num_tasks:
        assignments, total_skill_score = hungarian_task_assignment(skill_matrix, num_tasks)
    else:
        assignments, total_skill_score = maximize_skill_score_with_constraints(
            skill_matrix, num_tasks, len(absent_employees)
        )

    # Output: Print the Worker Task Assignments with corresponding skill scores
    print("\nWorker Task Assignments and Skill Scores:")
    worker_task_info = []
    for worker_id, task_id in assignments:
        worker_real_id = df.iloc[worker_id]['Worker ID']
        task_name = df.columns[task_id + 1]  # Skip 'Worker ID' column
        skill_score = df.iloc[worker_id, task_id + 1]
        worker_task_info.append([worker_real_id, task_name, skill_score])

    # Create a DataFrame for better table visualization
    assignments_df = pd.DataFrame(worker_task_info, columns=['Worker ID', 'Task', 'Skill Score'])
    print(assignments_df)

    # Output: Print the total maximized skill score
    print(f"\nTotal Maximized Skill Score: {total_skill_score}")

# Example usage
file_path = 'smalldataset.xlsx'
workers_assignment_problem_with_constraints(file_path)
