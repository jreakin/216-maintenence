import SwiftUI
import Supabase
import UserNotifications
import ARKit

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
    var beforeScan: String?
    var afterScan: String?
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

    private let supabaseClient = SupabaseClient(supabaseURL: "your_supabase_url", supabaseKey: "your_supabase_key")

    func fetchTasks() {
        supabaseClient.database.from("tasks").select().execute { result in
            switch result {
            case .success(let response):
                if let data = response.data as? [[String: Any]] {
                    self.tasks = data.compactMap { dict in
                        guard let id = dict["id"] as? Int,
                              let description = dict["description"] as? String,
                              let location = dict["location"] as? String,
                              let estimatedCost = dict["estimated_cost"] as? Double,
                              let status = dict["status"] as? String,
                              let priority = dict["priority"] as? String else { return nil }
                        let finalCost = dict["final_cost"] as? Double
                        let deadline = dict["deadline"] as? Date
                        let dependencies = dict["dependencies"] as? [Int]
                        let comments = dict["comments"] as? [String]
                        let attachments = dict["attachments"] as? [String]
                        let beforeScan = dict["before_scan"] as? String
                        let afterScan = dict["after_scan"] as? String
                        return Task(id: id, description: description, location: location, estimatedCost: estimatedCost, finalCost: finalCost, status: status, priority: priority, deadline: deadline, dependencies: dependencies, comments: comments, attachments: attachments, beforeScan: beforeScan, afterScan: afterScan)
                    }
                }
            case .failure(let error):
                print("Error fetching tasks: \(error.localizedDescription)")
            }
        }
    }

    func fetchUsers() {
        supabaseClient.database.from("users").select().execute { result in
            switch result {
            case .success(let response):
                if let data = response.data as? [[String: Any]] {
                    self.users = data.compactMap { dict in
                        guard let id = dict["id"] as? Int,
                              let username = dict["username"] as? String,
                              let role = dict["role"] as? String else { return nil }
                        return User(id: id, username: username, role: role)
                    }
                }
            case .failure(let error):
                print("Error fetching users: \(error.localizedDescription)")
            }
        }
    }

    func updateTaskStatus(taskId: Int, status: String) {
        supabaseClient.database.from("tasks").update(values: ["status": status]).eq(column: "id", value: taskId).execute { result in
            switch result {
            case .success:
                self.fetchTasks()
            case .failure(let error):
                print("Error updating task status: \(error.localizedDescription)")
            }
        }
    }

    func updateTaskPriority(taskId: Int, priority: String) {
        supabaseClient.database.from("tasks").update(values: ["priority": priority]).eq(column: "id", value: taskId).execute { result in
            switch result {
            case .success:
                self.fetchTasks()
            case .failure(let error):
                print("Error updating task priority: \(error.localizedDescription)")
            }
        }
    }

    func addCommentToTask(taskId: Int, comment: String) {
        supabaseClient.database.from("tasks").update(values: ["comments": comment]).eq(column: "id", value: taskId).execute { result in
            switch result {
            case .success:
                self.fetchTasks()
            case .failure(let error):
                print("Error adding comment to task: \(error.localizedDescription)")
            }
        }
    }

    func addAttachmentToTask(taskId: Int, attachment: String) {
        supabaseClient.database.from("tasks").update(values: ["attachments": attachment]).eq(column: "id", value: taskId).execute { result in
            switch result {
            case .success:
                self.fetchTasks()
            case .failure(let error):
                print("Error adding attachment to task: \(error.localizedDescription)")
            }
        }
    }

    func validateAddress(address: String, completion: @escaping (String?) -> Void) {
        // Validate address using backend API
    }

    func scanReceipt(file: Data, completion: @escaping (String?) -> Void) {
        // Scan receipt using backend API
    }

    func registerUser(username: String, password: String, role: String, completion: @escaping (Bool) -> Void) {
        supabaseClient.auth.signUp(email: username, password: password) { result in
            switch result {
            case .success:
                self.supabaseClient.database.from("users").insert(values: ["username": username, "role": role]).execute { result in
                    switch result {
                    case .success:
                        completion(true)
                    case .failure(let error):
                        print("Error registering user: \(error.localizedDescription)")
                        completion(false)
                    }
                }
            case .failure(let error):
                print("Error signing up user: \(error.localizedDescription)")
                completion(false)
            }
        }
    }

    func loginUser(username: String, password: String, completion: @escaping (Bool) -> Void) {
        supabaseClient.auth.signIn(email: username, password: password) { result in
            switch result {
            case .success:
                self.currentUser = User(id: 0, username: username, role: "") // Update with actual user data
                completion(true)
            case .failure(let error):
                print("Error logging in user: \(error.localizedDescription)")
                completion(false)
            }
        }
    }

    // Role-based access control
    func hasPermission(for role: String) -> Bool {
        guard let currentUser = currentUser else { return false }
        let roleHierarchy = ["Super Admin": 4, "Office Admin": 3, "Dispatcher": 2, "Employee": 1]
        return roleHierarchy[currentUser.role] ?? 0 >= roleHierarchy[role] ?? 0
    }

    // Push notifications
    func sendPushNotification(title: String, body: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = UNNotificationSound.default

        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request, withCompletionHandler: nil)
    }

    // ARKit room scanning
    func captureRoomLayout() -> String {
        // Implement ARKit room scanning and return the captured layout data as a string
        return "room_layout_data"
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
            if let beforeScan = task.beforeScan {
                Text("Before Scan: \(beforeScan)")
                    .font(.subheadline)
            }
            if let afterScan = task.afterScan {
                Text("After Scan: \(afterScan)")
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
