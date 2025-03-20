def quiz():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout
            xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            android:padding="16dp">

            <TextView
                android:id="@+id/question"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Question goes here"
                android:textSize="18sp"
                android:paddingBottom="10dp" />

            <RadioGroup
                android:id="@+id/optionsGroup"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content">

                <RadioButton
                    android:id="@+id/option1"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Option 1" />

                <RadioButton
                    android:id="@+id/option2"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Option 2" />

                <RadioButton
                    android:id="@+id/option3"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Option 3" />

                <RadioButton
                    android:id="@+id/option4"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Option 4" />
            </RadioGroup>

            <Button
                android:id="@+id/btnSubmit"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Submit"
                android:layout_marginTop="10dp" />

            <TextView
                android:id="@+id/result"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text=""
                android:textSize="16sp"
                android:paddingTop="10dp" />
        </LinearLayout>
        """,
        """
        package com.example.test;

        import android.os.Bundle;
        import android.view.View;
        import android.widget.*;
        import androidx.appcompat.app.AppCompatActivity;

        public class MainActivity extends AppCompatActivity {
            TextView questionView, resultView;
            RadioGroup optionsGroup;
            RadioButton option1, option2, option3, option4;
            Button btnSubmit;

            int currentQuestionIndex = 0, score = 0;

            String[][] questions = {
                    {"What is the capital of France?", "Paris", "London", "Berlin", "Madrid", "Paris"},
                    {"Who developed Java?", "James Gosling", "Dennis Ritchie", "Bjarne Stroustrup", "Guido van Rossum", "James Gosling"},
                    {"Which planet is known as the Red Planet?", "Earth", "Mars", "Jupiter", "Saturn", "Mars"}
            };

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                questionView = findViewById(R.id.question);
                resultView = findViewById(R.id.result);
                optionsGroup = findViewById(R.id.optionsGroup);
                option1 = findViewById(R.id.option1);
                option2 = findViewById(R.id.option2);
                option3 = findViewById(R.id.option3);
                option4 = findViewById(R.id.option4);
                btnSubmit = findViewById(R.id.btnSubmit);

                loadQuestion();

                btnSubmit.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        checkAnswer();
                    }
                });
            }

            private void loadQuestion() {
                if (currentQuestionIndex < questions.length) {
                    questionView.setText(questions[currentQuestionIndex][0]);
                    option1.setText(questions[currentQuestionIndex][1]);
                    option2.setText(questions[currentQuestionIndex][2]);
                    option3.setText(questions[currentQuestionIndex][3]);
                    option4.setText(questions[currentQuestionIndex][4]);
                    optionsGroup.clearCheck();
                    resultView.setText("");
                } else {
                    resultView.setText("Quiz finished! Your score: " + score + "/" + questions.length);
                    btnSubmit.setEnabled(false);
                }
            }

            private void checkAnswer() {
                int selectedId = optionsGroup.getCheckedRadioButtonId();
                if (selectedId == -1) {
                    resultView.setText("Please select an answer!");
                    return;
                }

                RadioButton selectedOption = findViewById(selectedId);
                String selectedAnswer = selectedOption.getText().toString();
                String correctAnswer = questions[currentQuestionIndex][5];

                if (selectedAnswer.equals(correctAnswer)) {
                    score++;
                }

                currentQuestionIndex++;
                loadQuestion();
            }
        }
        """
    ]