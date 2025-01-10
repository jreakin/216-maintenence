import SwiftUI

struct Task: Identifiable {
    var id: Int
    var description: String
    var location: String
    var estimatedCost: Double
    var finalCost: Double?
    var status: String
    var priority: String
    var deadline: Date?
    var dependencies: [Int]?
    var comments: [String]?
    var attachments: [String]?
}

struct User: Identifiable {
    var id: Int
    var username: String
    var role: String
}

class TaskViewModel: ObservableObject {
    @Published var tasks: [Task] = []
    @Published var users: [User] = []
    @Published var currentUser: User?

    func fetchTasks() {
        // Fetch tasks from backend API
    }

    func fetchUsers() {
        // Fetch users from backend API
    }

    func updateTaskStatus(taskId: Int, status: String) {
        // Update task status in backend API
    }

    func updateTaskPriority(taskId: Int, priority: String) {
        // Update task priority in backend API
    }

    func addCommentToTask(taskId: Int, comment: String) {
        // Add comment to task in backend API
    }

    func addAttachmentToTask(taskId: Int, attachment: String) {
        // Add attachment to task in backend API
    }

    func validateAddress(address: String, completion: @escaping (String?) -> Void) {
        // Validate address using backend API
    }

    func scanReceipt(file: Data, completion: @escaping (String?) -> Void) {
        // Scan receipt using backend API
    }
}

struct ContentView: View {
    @ObservedObject var viewModel = TaskViewModel()

    var body: some View {
        NavigationView {
            List(viewModel.tasks) { task in
                TaskRow(task: task)
            }
            .navigationBarTitle("Tasks")
            .onAppear {
                viewModel.fetchTasks()
            }
        }
    }
}

struct TaskRow: View {
    var task: Task

    var body: some View {
        VStack(alignment: .leading) {
            Text(task.description)
                .font(.headline)
            Text("Location: \(task.location)")
                .font(.subheadline)
            Text("Estimated Cost: \(task.estimatedCost)")
                .font(.subheadline)
            if let finalCost = task.finalCost {
                Text("Final Cost: \(finalCost)")
                    .font(.subheadline)
            }
            Text("Status: \(task.status)")
                .font(.subheadline)
            Text("Priority: \(task.priority)")
                .font(.subheadline)
            if let deadline = task.deadline {
                Text("Deadline: \(deadline, formatter: dateFormatter)")
                    .font(.subheadline)
            }
            if let dependencies = task.dependencies {
                Text("Dependencies: \(dependencies.map { String($0) }.joined(separator: ", "))")
                    .font(.subheadline)
            }
            if let comments = task.comments {
                Text("Comments: \(comments.joined(separator: ", "))")
                    .font(.subheadline)
            }
            if let attachments = task.attachments {
                Text("Attachments: \(attachments.joined(separator: ", "))")
                    .font(.subheadline)
            }
        }
    }
}

let dateFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .short
    formatter.timeStyle = .short
    return formatter
}()
