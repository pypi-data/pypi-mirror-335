def calculator():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            android:gravity="center"
            android:padding="20dp">

            <TextView
                android:id="@+id/tvResult"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Result"
                android:textSize="24sp"
                android:gravity="center"
                android:padding="10dp" />

            <EditText
                android:id="@+id/etInput"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:inputType="none"
                android:textSize="20sp"
                android:gravity="center" />

            <GridLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:columnCount="4"
                android:rowCount="5"
                android:paddingTop="20dp">

                <Button android:text="7" android:onClick="onNumberClick"/>
                <Button android:text="8" android:onClick="onNumberClick"/>
                <Button android:text="9" android:onClick="onNumberClick"/>
                <Button android:text="/" android:onClick="onOperatorClick"/>

                <Button android:text="4" android:onClick="onNumberClick"/>
                <Button android:text="5" android:onClick="onNumberClick"/>
                <Button android:text="6" android:onClick="onNumberClick"/>
                <Button android:text="*" android:onClick="onOperatorClick"/>

                <Button android:text="1" android:onClick="onNumberClick"/>
                <Button android:text="2" android:onClick="onNumberClick"/>
                <Button android:text="3" android:onClick="onNumberClick"/>
                <Button android:text="-" android:onClick="onOperatorClick"/>

                <Button android:text="0" android:onClick="onNumberClick"/>
                <Button android:text="C" android:onClick="onClear"/>
                <Button android:text="=" android:onClick="onEquals"/>
                
                <Button android:text="+" android:onClick="onOperatorClick"/>

            </GridLayout>

        </LinearLayout>
        """,
        """
        package com.example.program3calc;

        import android.os.Bundle;
        import android.view.View;
        import android.widget.Button;
        import android.widget.EditText;
        import android.widget.TextView;
        import androidx.appcompat.app.AppCompatActivity;

        public class MainActivity extends AppCompatActivity {
            private EditText etInput;
            private TextView tvResult;
            private String input = "";
            private double num1 = 0, num2 = 0;
            private char operator = ' ';

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                etInput = findViewById(R.id.etInput);
                tvResult = findViewById(R.id.tvResult);
            }

            public void onNumberClick(View view) {
                Button button = (Button) view;
                input += button.getText().toString();
                etInput.setText(input);
            }

            public void onOperatorClick(View view) {
                if (!input.isEmpty()) {
                    num1 = Double.parseDouble(input);
                    Button button = (Button) view;
                    operator = button.getText().toString().charAt(0);
                    input = "";
                    etInput.setText("");
                }
            }

            public void onEquals(View view) {
                if (!input.isEmpty() && operator != ' ') {
                    num2 = Double.parseDouble(input);
                    double result = calculate(num1, num2, operator);
                    tvResult.setText("Result: " + result);
                    input = String.valueOf(result);  // Store result for further operations
                    operator = ' ';
                }
            }

            public void onClear(View view) {
                input = "";
                num1 = 0;
                num2 = 0;
                operator = ' ';
                etInput.setText("");
                tvResult.setText("Result");
            }

            private double calculate(double a, double b, char op) {
                switch (op) {
                    case '+': return a + b;
                    case '-': return a - b;
                    case '*': return a * b;
                    case '/': return (b != 0) ? a / b : 0; // Avoid division by zero
                    default: return 0;
                }
            }
        }
        """
    ]