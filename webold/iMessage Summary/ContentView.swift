//
//  ContentView.swift
//  iMessage Summary
//
//  Created by Jeffrey Kim on 12/30/24.
//

import SwiftUI

struct ContentView: View {
    @State private var chatName: String = "" // State variable for input
    @State private var outputText: String = "" // State variable for output
    @State private var navigate: Bool = false
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) { // Vertical layout
                Text("iMessage Summarizer")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                Text("Select a chat")
                    .fontWeight(.bold)
                
                TextField("Enter chat name", text: $chatName)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding()
                Button(action: {
                    navigate = true
                }) {
                    Text("Submit")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                
                NavigationLink(
                    destination: OutputView(initialChatName: chatName),
                    isActive: $navigate
                ) {
                    EmptyView()
                }
                .hidden()
            }
            .padding()
            .frame(width: 400, height: 300) // Set a fixed size for the window
        }
    }
}

struct OutputView: View {
    @State private var chatName: String
    @State private var numMessages: String
    @State private var numParagraphs: String
    
    init(initialChatName: String) {
        _chatName = State(initialValue: initialChatName)
        _numMessages = State(initialValue: "50")
        _numParagraphs = State(initialValue: "4")
    }
    
    var body: some View {
        HStack(alignment: .top, spacing: 20) { // Horizontal layout for three columns
            // Column 1
            VStack(spacing: 10) {
                Text("Chat")
                    .font(.headline)
                TextField(chatName, text: $chatName)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding()
            }
            .frame(maxWidth: .infinity) // Make each column flexible
            
            Divider()
                .frame(height: nil)
                .background(Color.gray)
            
            // Column 2
            VStack(spacing: 10) {
                Text("# Messages")
                    .font(.headline)
                
                TextField("50", text: $numMessages)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding()
                
                Text("# Paragraphs")
                    .font(.headline)
                
                TextField("3", text: $numParagraphs)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding()
                
                Spacer()
                
                Button(action: {}) {
                    Text("Generate")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
            }
            .frame(maxWidth: .infinity)
            
            Divider()
                .frame(height: nil)
                .background(Color.gray)
            
            // Column 3
            VStack(spacing: 10) {
                Text("Summary")
                    .font(.headline)
                ScrollView {
                    Text("asdfiojsadoifjasdofjaosifjewaoijfasdfiojsadoifjasdofjaosifjewaoijfasdfiojsadoifjasdofjaosifjewaoijfasdfiojsadoifjasdofjaosifjewaoijfasdfiojsadoifjasdofjaosifjewaoijfasdfiojsadoifjasdofjaosifjewaoijfasdfiojsadoifjasdofjaosifjewaoijfasdfiojsadoifjasdofjaosifjewaoijf")
                        .padding()
                        .frame(minHeight: 200)  // Set the height of the Text box
                        .border(Color.gray)     // Add a border around the text box for clarity
                }
                    .frame(height: 200)
            }
            .frame(maxWidth: .infinity)
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
